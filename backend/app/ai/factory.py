from typing import Dict, Type
from .base import BaseAgent
from .agents.content_analysis import ContentAnalysisAgent
from .agents.competitive_intelligence import CompetitiveIntelligenceAgent
from .agents.objection_handling import ObjectionHandlingAgent
from .agents.use_case import UseCaseGenerationAgent
from .agents.aggregator import AggregatorOrchestrationAgent


class AIAgentFactory:
    """Factory for creating and managing AI agents."""
    
    _agents: Dict[str, Type[BaseAgent]] = {
        "content_analysis": ContentAnalysisAgent,
        "competitive_intelligence": CompetitiveIntelligenceAgent,
        "objection_handling": ObjectionHandlingAgent,
        "use_case": UseCaseGenerationAgent,
        "aggregator": AggregatorOrchestrationAgent
    }
    
    @classmethod
    def get_agent(cls, agent_type: str) -> BaseAgent:
        """Get an instance of the specified agent type."""
        if agent_type not in cls._agents:
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Available types: {list(cls._agents.keys())}"
            )
        
        return cls._agents[agent_type]()
    
    @classmethod
    def list_available_agents(cls) -> list[str]:
        """List all available agent types."""
        return list(cls._agents.keys())
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type."""
        if not issubclass(agent_class, BaseAgent):
            raise ValueError("Agent class must inherit from BaseAgent")
        
        cls._agents[agent_type] = agent_class 