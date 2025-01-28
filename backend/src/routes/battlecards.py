from fastapi import APIRouter
from ..agents.orchestration_agent import OrchestrationAgent
from ..models.battlecard import Battlecard

router = APIRouter()

@router.get("/")
def get_battlecards():
    # Retrieve all battlecards from the database
    return {"battlecards": "List of battlecards could be here"}

@router.post("/auto-generate")
def auto_generate_battlecard():
    orchestrator = OrchestrationAgent()
    agent_output = orchestrator.run_all()
    # Create or update a Battlecard object with the returned data
    new_card = Battlecard(
        competitor_summary=agent_output["summarized_competitors"],
        competitive_analysis=str(agent_output["competitive_analysis"]),
        objections_responses=agent_output["objections_responses"]
    )
    # Normally you'd save to DB and return it
    return {"message": "Battlecard generated", "data": new_card.dict()} 