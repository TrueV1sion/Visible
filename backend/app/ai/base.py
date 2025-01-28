from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import anthropic
import openai
from ..core.config import settings


class BaseAgent(ABC):
    """Base class for all AI agents in the system."""
    
    def __init__(self):
        self.anthropic_client = anthropic.Client(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.openai_client = openai.Client(
            api_key=settings.OPENAI_API_KEY
        )
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results."""
        pass
    
    async def _call_claude(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1000
    ) -> str:
        """Call Claude API with proper error handling."""
        try:
            message = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content
        except Exception as e:
            # Log error and try fallback
            print(f"Claude API error: {str(e)}")
            return await self._call_gpt4(prompt, system, max_tokens)
    
    async def _call_gpt4(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1000
    ) -> str:
        """Call GPT-4 API as fallback."""
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Both Claude and GPT-4 APIs failed: {str(e)}")
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data format."""
        return True  # Override in subclasses
    
    def _format_output(self, raw_output: str) -> Dict[str, Any]:
        """Format the raw AI output into structured data."""
        return {"result": raw_output}  # Override in subclasses 