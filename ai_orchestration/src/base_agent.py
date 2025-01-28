from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

class BaseAgent(ABC):
    """Base class for all AI agents in the orchestration system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            config: Optional configuration dictionary for the agent
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for the agent."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return results.
        
        Args:
            input_data: Dictionary containing input data for processing
            
        Returns:
            Dictionary containing processed results
        """
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data format.
        
        Args:
            input_data: Dictionary containing input data to validate
            
        Returns:
            Boolean indicating if input is valid
        """
        return True  # Override in subclasses
    
    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """
        Format raw output into standardized structure.
        
        Args:
            raw_output: Raw output from processing
            
        Returns:
            Dictionary containing formatted output
        """
        return {"result": raw_output}  # Override in subclasses 