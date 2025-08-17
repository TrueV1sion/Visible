from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ....core.security import get_current_user, require_role
from ....core.exceptions import ResourceNotFoundError, ValidationError, create_http_exception
from ....db.base import get_db
from ....models.user import User, UserRole
from ....models.battlecard import Battlecard, BattlecardVersion, BattlecardStatus
from ....schemas.battlecard import (
    Battlecard as BattlecardSchema,
    BattlecardCreate,
    BattlecardUpdate
)
from ....schemas.validation import BattlecardGenerationRequestSchema, AIProcessingOptionsSchema
from ....services.ai_orchestrator import ai_orchestrator

router = APIRouter()


@router.get("", response_model=List[BattlecardSchema])
async def list_battlecards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    status_filter: Optional[BattlecardStatus] = Query(None),
    competitor_filter: Optional[str] = Query(None)
) -> Any:
    """Retrieve battlecards with filtering and pagination."""
    try:
        query = db.query(Battlecard)
        
        # Apply role-based filtering
        if current_user.role in [UserRole.VIEWER, UserRole.SALES]:
            # Only show published battlecards and own drafts
            query = query.filter(
                (Battlecard.status == BattlecardStatus.PUBLISHED) |
                (Battlecard.created_by_id == current_user.id)
            )
        
        # Apply filters
        if status_filter:
            query = query.filter(Battlecard.status == status_filter)
        
        if competitor_filter:
            query = query.join(Battlecard.competitor).filter(
                Competitor.name.ilike(f"%{competitor_filter}%")
            )
        
        # Execute query with pagination
        battlecards = query.offset(skip).limit(limit).all()
        
        return battlecards
        
    except Exception as e:
        raise create_http_exception(
            ValidationError(f"Failed to fetch battlecards: {str(e)}")
        )


@router.post("/generate", response_model=BattlecardSchema)
async def generate_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'editor', 'marketing'])),
    request_data: BattlecardGenerationRequestSchema,
    ai_options: Optional[AIProcessingOptionsSchema] = None
) -> Any:
    """Generate a new battlecard using AI."""
    try:
        # Prepare AI generation options
        options = {}
        if ai_options:
            options = {
                "model_preference": ai_options.model_preference,
                "complexity_level": ai_options.complexity_level,
                "max_tokens": ai_options.max_tokens,
                "temperature": ai_options.temperature,
                "include_sources": ai_options.include_sources,
                "include_sections": request_data.include_sections
            }
        
        # Generate battlecard using AI orchestrator
        result = await ai_orchestrator.generate_battlecard(
            competitor_info=request_data.competitor_info.dict(),
            product_segment=request_data.product_segment,
            focus_areas=request_data.focus_areas,
            options=options
        )
        
        if result.get('status') != 'success':
            raise AIGenerationError("Battlecard generation failed")
        
        # Create battlecard in database
        battlecard_data = result['data']['battlecard']
        battlecard = Battlecard(
            title=f"{request_data.competitor_info.name} Competitive Analysis",
            description=f"AI-generated battlecard for {request_data.competitor_info.name}",
            status=BattlecardStatus.DRAFT,
            company_overview=battlecard_data.get('overview', {}).get('description'),
            target_market=request_data.product_segment,
            competitive_analysis=battlecard_data.get('competitive_analysis'),
            product_features=battlecard_data.get('product_features'),
            pricing_structure=battlecard_data.get('pricing_comparison'),
            use_cases=battlecard_data.get('use_cases'),
            objection_handling=battlecard_data.get('objection_handling'),
            created_by_id=current_user.id,
            last_modified_by_id=current_user.id
        )
        
        # Create initial version
        version = BattlecardVersion(
            version_number=1,
            content=result['data'],
            created_by_id=current_user.id
        )
        battlecard.versions.append(version)
        
        db.add(battlecard)
        db.commit()
        db.refresh(battlecard)
        
        return battlecard
        
    except AIGenerationError as e:
        raise create_http_exception(e)
    except Exception as e:
        raise create_http_exception(
            AIGenerationError(f"Battlecard generation failed: {str(e)}")
        )


@router.get("/{battlecard_id}", response_model=BattlecardSchema)
async def read_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    battlecard_id: int
) -> Any:
    """Get battlecard by ID with access control."""
    try:
        battlecard = db.query(Battlecard).filter(
            Battlecard.id == battlecard_id
        ).first()
        
        if not battlecard:
            raise ResourceNotFoundError("Battlecard", str(battlecard_id))
        
        # Check access permissions
        if (battlecard.status != BattlecardStatus.PUBLISHED and 
            battlecard.created_by_id != current_user.id and
            current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]):
            raise AuthorizationError("Access denied to this battlecard")
        
        return battlecard
        
    except (ResourceNotFoundError, AuthorizationError) as e:
        raise create_http_exception(e)


@router.put("/{battlecard_id}", response_model=BattlecardSchema)
async def update_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'editor', 'marketing'])),
    battlecard_id: int,
    battlecard_in: BattlecardUpdate
) -> Any:
    """Update battlecard with version control."""
    try:
        battlecard = db.query(Battlecard).filter(
            Battlecard.id == battlecard_id
        ).first()
        
        if not battlecard:
            raise ResourceNotFoundError("Battlecard", str(battlecard_id))
        
        # Check edit permissions
        if (battlecard.created_by_id != current_user.id and
            current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]):
            raise AuthorizationError("Cannot edit this battlecard")
        
        # Update battlecard fields
        update_data = battlecard_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(battlecard, field, value)
        
        battlecard.last_modified_by_id = current_user.id
        
        # Create new version
        new_version_number = len(battlecard.versions) + 1
        version = BattlecardVersion(
            version_number=new_version_number,
            content=update_data,
            created_by_id=current_user.id
        )
        battlecard.versions.append(version)
        
        db.commit()
        db.refresh(battlecard)
        
        return battlecard
        
    except (ResourceNotFoundError, AuthorizationError) as e:
        raise create_http_exception(e)


@router.delete("/{battlecard_id}")
async def delete_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin'])),
    battlecard_id: int
) -> Any:
    """Delete battlecard (admin only)."""
    try:
        battlecard = db.query(Battlecard).filter(
            Battlecard.id == battlecard_id
        ).first()
        
        if not battlecard:
            raise ResourceNotFoundError("Battlecard", str(battlecard_id))
        
        db.delete(battlecard)
        db.commit()
        
        return {"status": "success", "message": "Battlecard deleted"}
        
    except ResourceNotFoundError as e:
        raise create_http_exception(e)


@router.post("/{battlecard_id}/regenerate-section")
async def regenerate_section(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'editor', 'marketing'])),
    battlecard_id: int,
    section: str,
    options: Optional[AIProcessingOptionsSchema] = None
) -> Any:
    """Regenerate a specific section of a battlecard."""
    try:
        battlecard = db.query(Battlecard).filter(
            Battlecard.id == battlecard_id
        ).first()
        
        if not battlecard:
            raise ResourceNotFoundError("Battlecard", str(battlecard_id))
        
        # Validate section
        valid_sections = [
            'overview', 'competitive_analysis', 'strengths_weaknesses',
            'pricing_comparison', 'objection_handling', 'winning_strategies'
        ]
        if section not in valid_sections:
            raise ValidationError(f"Invalid section. Must be one of: {valid_sections}")
        
        # Prepare regeneration input
        regen_input = {
            "battlecard_id": battlecard_id,
            "section": section,
            "current_content": getattr(battlecard, section.replace('_', '_'), {}),
            "competitor_info": {
                "name": battlecard.competitor.name if battlecard.competitor else "Unknown",
                "id": battlecard.competitor_id
            },
            "context": {
                "product_segment": battlecard.target_market,
                "focus_regeneration": True
            }
        }
        
        # Generate new section content
        ai_options = options.dict() if options else {}
        result = await ai_orchestrator.process_with_agent(
            "content_analysis",
            regen_input,
            ai_options
        )
        
        if result.get('status') != 'success':
            raise AIGenerationError(f"Failed to regenerate section: {section}")
        
        # Update battlecard with new section content
        new_content = result['data']
        setattr(battlecard, section, new_content)
        battlecard.last_modified_by_id = current_user.id
        
        # Create new version
        new_version_number = len(battlecard.versions) + 1
        version = BattlecardVersion(
            version_number=new_version_number,
            content={section: new_content},
            created_by_id=current_user.id
        )
        battlecard.versions.append(version)
        
        db.commit()
        db.refresh(battlecard)
        
        return {
            "status": "success",
            "section": section,
            "content": new_content,
            "version": new_version_number
        }
        
    except (ResourceNotFoundError, ValidationError, AIGenerationError) as e:
        raise create_http_exception(e)


@router.get("/ai/status")
async def get_ai_status(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get AI orchestrator status."""
    try:
        status = await ai_orchestrator.get_status()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI status: {str(e)}"
        )