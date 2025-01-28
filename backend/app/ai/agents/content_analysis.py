from typing import Any, Dict, List
import json
from ..base import BaseAgent


class ContentAnalysisAgent(BaseAgent):
    """Agent for analyzing and summarizing content for battlecards."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw content and generate structured summaries."""
        if not self._validate_input(input_data):
            raise ValueError("Invalid input data format")

        # Prepare system prompt
        system_prompt = """
        You are an expert content analyst specializing in creating battlecards 
        for sales and marketing teams. Your task is to analyze the provided 
        content and extract key information in a structured format suitable 
        for battlecards.
        
        Focus on:
        1. Company and product positioning
        2. Key differentiators and value propositions
        3. Target market segments and use cases
        4. Competitive analysis points
        5. Common objections and responses
        """

        # Prepare content analysis prompt
        analysis_prompt = self._prepare_analysis_prompt(input_data)
        
        # Get AI analysis
        raw_analysis = await self._call_claude(
            prompt=analysis_prompt,
            system=system_prompt,
            max_tokens=2000
        )
        
        # Format and validate the output
        return self._format_output(raw_analysis)

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that input contains required fields."""
        required_fields = ["content", "content_type"]
        return all(field in input_data for field in required_fields)

    def _prepare_analysis_prompt(self, input_data: Dict[str, Any]) -> str:
        """Prepare the prompt based on content type."""
        content = input_data["content"]
        content_type = input_data["content_type"]
        
        prompts = {
            "company_overview": """
                Analyze the following company information and extract:
                - Core value proposition
                - Key market positioning
                - Primary industry focus
                - Company strengths
                
                Content:
                {content}
            """,
            "competitor": """
                Analyze the following competitor information and identify:
                - Key differentiators
                - Strengths and weaknesses
                - Competitive advantages
                - Market positioning
                
                Content:
                {content}
            """,
            "product": """
                Analyze the following product information and extract:
                - Key features and benefits
                - Target use cases
                - Technical specifications
                - Integration capabilities
                
                Content:
                {content}
            """
        }
        
        return prompts.get(
            content_type,
            "Analyze the following content:\n{content}"
        ).format(content=content)

    def _format_output(self, raw_output: str) -> Dict[str, Any]:
        """Format the AI output into structured data."""
        try:
            # Attempt to parse if output is JSON
            return json.loads(raw_output)
        except json.JSONDecodeError:
            # If not JSON, structure the raw text
            return {
                "summary": raw_output,
                "structured_data": self._extract_structured_data(raw_output)
            }
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from raw text output."""
        # Basic extraction of bullet points and sections
        lines = text.split("\n")
        current_section = "general"
        structured_data = {"general": []}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            if line.endswith(":") and not line.startswith("-"):
                current_section = line[:-1].lower()
                structured_data[current_section] = []
            # Check if line is a bullet point
            elif line.startswith("-"):
                structured_data[current_section].append(
                    line[1:].strip()
                )
            else:
                structured_data[current_section].append(line)
        
        return structured_data 