from typing import Any, Dict, List, Optional
import json
from datetime import datetime
from ..base import BaseAgent


class CompetitiveIntelligenceAgent(BaseAgent):
    """Agent for monitoring and analyzing competitor information."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process competitor data and generate insights."""
        if not self._validate_input(input_data):
            raise ValueError("Invalid input data format")

        # Prepare system prompt
        system_prompt = """
        You are an expert competitive intelligence analyst. Your task is to 
        analyze competitor information and identify key insights, changes, 
        and strategic implications. Focus on actionable intelligence that 
        can be used in sales and marketing battlecards.
        
        Provide analysis in the following areas:
        1. Product/Feature comparison
        2. Pricing analysis
        3. Market positioning
        4. Strengths and weaknesses
        5. Competitive advantages/disadvantages
        6. Recent changes and their implications
        """

        # Prepare competitor analysis prompt
        analysis_prompt = self._prepare_analysis_prompt(input_data)
        
        # Get AI analysis
        raw_analysis = await self._call_claude(
            prompt=analysis_prompt,
            system=system_prompt,
            max_tokens=2000
        )
        
        # Format and structure the output
        return self._format_output(raw_analysis)

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that input contains required competitor data."""
        required_fields = ["competitor_name", "data_points"]
        return all(field in input_data for field in required_fields)

    def _prepare_analysis_prompt(self, input_data: Dict[str, Any]) -> str:
        """Prepare the analysis prompt based on competitor data."""
        competitor_name = input_data["competitor_name"]
        data_points = input_data["data_points"]
        historical_data = input_data.get("historical_data", [])
        
        prompt = f"""
        Analyze the following information about {competitor_name}:

        Current Data Points:
        {json.dumps(data_points, indent=2)}

        Historical Context:
        {json.dumps(historical_data, indent=2) if historical_data else "No historical data available"}

        Please provide:
        1. Key changes and trends
        2. Competitive positioning analysis
        3. Threat assessment
        4. Recommended counter-strategies
        5. Sales battlecard updates
        """
        
        return prompt

    def _format_output(self, raw_output: str) -> Dict[str, Any]:
        """Format the analysis output into structured data."""
        try:
            # Attempt to parse if output is JSON
            return json.loads(raw_output)
        except json.JSONDecodeError:
            # Structure the raw text output
            analysis = self._extract_analysis_sections(raw_output)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": analysis,
                "raw_insights": raw_output
            }
    
    def _extract_analysis_sections(self, text: str) -> Dict[str, List[str]]:
        """Extract and structure different sections of the analysis."""
        sections = {
            "changes_and_trends": [],
            "competitive_positioning": [],
            "threat_assessment": [],
            "counter_strategies": [],
            "battlecard_updates": []
        }
        
        current_section = None
        
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            lower_line = line.lower()
            if "changes" in lower_line or "trends" in lower_line:
                current_section = "changes_and_trends"
            elif "positioning" in lower_line:
                current_section = "competitive_positioning"
            elif "threat" in lower_line:
                current_section = "threat_assessment"
            elif "counter" in lower_line or "strateg" in lower_line:
                current_section = "counter_strategies"
            elif "battlecard" in lower_line:
                current_section = "battlecard_updates"
            elif current_section and line.startswith("-"):
                sections[current_section].append(line[1:].strip())
            elif current_section and line:
                sections[current_section].append(line)
        
        return sections

    async def get_competitor_updates(
        self,
        competitor_name: str,
        timeframe_days: Optional[int] = 30
    ) -> Dict[str, Any]:
        """Get recent updates about a specific competitor."""
        # This would typically integrate with external data sources
        # For now, we'll return a mock structure
        return {
            "competitor_name": competitor_name,
            "timeframe_days": timeframe_days,
            "updates": [],
            "last_checked": datetime.utcnow().isoformat()
        } 