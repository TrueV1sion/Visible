from typing import Any, Dict
import json
from .base_agent import BaseAgent

class InsightsAgent(BaseAgent):
    """Agent for generating general insights based on context."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Validate input
        # Prepare prompts if using a language model
        system_prompt = """
        You are an AI agent providing context-based insights.
        Analyze the provided information and generate suggestions or insights 
        for improving sales, marketing, or product strategies.
        """

        # input_data["options"] might hold minConfidence, maxResults, etc.
        user_prompt = f"Context: {json.dumps(input_data)}\n"
        raw_output = await self._call_claude(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=1500
        )

        # Return structured results (fake example)
        insights = self._format_output(raw_output)
        return insights

    def _format_output(self, raw_output: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            return {
                "insights": raw_output,
                "metadata": {}
            } 