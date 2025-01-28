from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.security import get_current_user
from ....db.base import get_db
from ....models.user import User, UserRole
from ....ai.factory import AIAgentFactory

router = APIRouter()


@router.post("/{agent_type}/process")
async def process_with_agent(
    *,
    agent_type: str,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process input data with the specified AI agent.
    """
    try:
        agent = AIAgentFactory.get_agent(agent_type)
        result = await agent.process(input_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}"
        )


@router.get("/agents")
async def list_agents(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List all available AI agents.
    """
    return {
        "available_agents": AIAgentFactory.list_available_agents()
    }


@router.post("/aggregator/search")
async def search_competitor(
    *,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Search and aggregate competitor information from multiple sources.
    """
    agent = AIAgentFactory.get_agent("aggregator")
    return await agent.process(input_data)


@router.post("/aggregator/monitor")
async def monitor_competitor(
    *,
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Set up continuous monitoring for a competitor.
    """
    # Get competitor details from DB
    competitor = db.query(Competitor).filter_by(id=competitor_id).first()
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )

    agent = AIAgentFactory.get_agent("aggregator")
    result = await agent.process({
        "competitor_name": competitor.name,
        "context": {
            "competitor_id": competitor_id,
            "monitoring": True,
            "user_id": current_user.id
        }
    })

    return result


@router.post("/competitive-analysis")
async def analyze_competitor(
    *,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze competitor information.
    """
    agent = AIAgentFactory.get_agent("competitive_intelligence")
    return await agent.process(input_data)


@router.post("/objection-handling")
async def handle_objection(
    *,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate response strategy for sales objection.
    """
    agent = AIAgentFactory.get_agent("objection_handling")
    return await agent.process(input_data)


@router.post("/use-case")
async def generate_use_case(
    *,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate customer use case.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    agent = AIAgentFactory.get_agent("use_case")
    return await agent.process(input_data)


@router.post("/analyze-content")
async def analyze_content(
    *,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze and structure content for battlecards.
    """
    agent = AIAgentFactory.get_agent("content_analysis")
    return await agent.process(input_data)


@router.post("/insights/generate")
async def generate_insights(
    *,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate AI-based insights given context.
    """
    # Example: "insights" agent or re-use an existing one
    agent = AIAgentFactory.get_agent("insights")
    result = await agent.process(input_data)

    # Return structured suggestions
    return result


@router.post("/insights/apply")
async def apply_insight(
    *,
    insight_id: str,
    target_battlecard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Apply a chosen insight to an existing battlecard.
    This is a stub. Insert real logic to:
      - Fetch the specified insight from DB or cache
      - Update the relevant battlecard section
      - Possibly re-run the battlecard generation pipeline
    """
    # Pseudocode:
    # insight = db.query(Insight).filter_by(id=insight_id).first()
    # if not insight:
    #     raise HTTPException(status_code=404, detail="Insight not found")
    #
    # bc = db.query(Battlecard).filter_by(id=target_battlecard_id).first()
    # bc.update_with_insight(insight)
    # db.commit()

    return {"message": f"Insight {insight_id} applied to battlecard {target_battlecard_id}"}


@router.post("/insights/discard")
async def discard_insight(
    *,
    insight_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Discard an insight, marking it as rejected or removing it from the DB.
    """
    # Pseudocode:
    # insight = db.query(Insight).filter_by(id=insight_id).first()
    # if insight:
    #     insight.status = "discarded"
    #     db.commit()
    # else:
    #     raise HTTPException(status_code=404, detail="Insight not found")

    return {"message": f"Insight {insight_id} discarded"} 