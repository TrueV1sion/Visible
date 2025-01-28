from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.security import get_current_user
from ....db.base import get_db
from ....models.user import User, UserRole
from ....models.battlecard import Battlecard, BattlecardVersion
from ....schemas.battlecard import (
    Battlecard as BattlecardSchema,
    BattlecardCreate,
    BattlecardUpdate
)

router = APIRouter()


@router.get("", response_model=List[BattlecardSchema])
def list_battlecards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve battlecards.
    """
    battlecards = db.query(Battlecard).offset(skip).limit(limit).all()
    return battlecards


@router.post("", response_model=BattlecardSchema)
def create_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    battlecard_in: BattlecardCreate
) -> Any:
    """
    Create new battlecard.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    battlecard = Battlecard(**battlecard_in.dict())
    battlecard.created_by_id = current_user.id
    battlecard.last_modified_by_id = current_user.id
    
    # Create initial version
    version = BattlecardVersion(
        version_number=1,
        content=battlecard_in.dict(),
        created_by_id=current_user.id
    )
    battlecard.versions.append(version)
    
    db.add(battlecard)
    db.commit()
    db.refresh(battlecard)
    return battlecard


@router.get("/{battlecard_id}", response_model=BattlecardSchema)
def read_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    battlecard_id: int
) -> Any:
    """
    Get battlecard by ID.
    """
    battlecard = db.query(Battlecard).filter(
        Battlecard.id == battlecard_id
    ).first()
    if not battlecard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battlecard not found"
        )
    return battlecard


@router.put("/{battlecard_id}", response_model=BattlecardSchema)
def update_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    battlecard_id: int,
    battlecard_in: BattlecardUpdate
) -> Any:
    """
    Update battlecard.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    battlecard = db.query(Battlecard).filter(
        Battlecard.id == battlecard_id
    ).first()
    if not battlecard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battlecard not found"
        )
    
    # Update battlecard
    for field, value in battlecard_in.dict(exclude_unset=True).items():
        setattr(battlecard, field, value)
    battlecard.last_modified_by_id = current_user.id
    
    # Create new version
    version = BattlecardVersion(
        version_number=len(battlecard.versions) + 1,
        content=battlecard_in.dict(),
        created_by_id=current_user.id
    )
    battlecard.versions.append(version)
    
    db.add(battlecard)
    db.commit()
    db.refresh(battlecard)
    return battlecard


@router.delete("/{battlecard_id}")
def delete_battlecard(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    battlecard_id: int
) -> Any:
    """
    Delete battlecard.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    battlecard = db.query(Battlecard).filter(
        Battlecard.id == battlecard_id
    ).first()
    if not battlecard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battlecard not found"
        )
    
    db.delete(battlecard)
    db.commit()
    return {"status": "success"} 