from typing import Any, Dict, List
import json
from ..base import BaseAgent


class ObjectionHandlingAgent(BaseAgent):
    """Agent for managing and generating responses to sales objections."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process objection data and generate structured responses."""
        if not self._validate_input(input_data):
            raise ValueError("Invalid input data format")

        # Prepare system prompt
        system_prompt = """
        You are an expert sales consultant specializing in handling objections.
        Your task is to analyze sales objections and provide strategic, 
        effective responses that align with the company's value proposition
        and competitive advantages.
        
        For each objection, provide:
        1. A clear, concise response
        2. Supporting talking points
        3. Relevant customer success stories or metrics
        4. Follow-up questions to better understand concerns
        5. Alternative approaches if initial response isn't effective
        """

        # Prepare objection analysis prompt
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
        """Validate that input contains required objection data."""
        required_fields = ["objection", "context"]
        return all(field in input_data for field in required_fields)

    def _prepare_analysis_prompt(self, input_data: Dict[str, Any]) -> str:
        """Prepare the analysis prompt based on objection data."""
        objection = input_data["objection"]
        context = input_data["context"]
        success_stories = input_data.get("success_stories", [])
        competitor_info = input_data.get("competitor_info", {})
        
        prompt = f"""
        Analyze and provide a response strategy for the following objection:

        Objection:
        {objection}

        Context:
        {json.dumps(context, indent=2)}

        Success Stories:
        {json.dumps(success_stories, indent=2) if success_stories else "No success stories provided"}

        Competitor Information:
        {json.dumps(competitor_info, indent=2) if competitor_info else "No competitor information provided"}

        Please provide:
        1. Initial Response
        2. Key Talking Points
        3. Supporting Evidence
        4. Discovery Questions
        5. Alternative Approaches
        """
        
        return prompt

    def _format_output(self, raw_output: str) -> Dict[str, Any]:
        """Format the analysis output into structured data."""
        try:
            # Attempt to parse if output is JSON
            return json.loads(raw_output)
        except json.JSONDecodeError:
            # Structure the raw text output
            return {
                "response_strategy": self._extract_response_strategy(raw_output)
            }
    
    def _extract_response_strategy(self, text: str) -> Dict[str, List[str]]:
        """Extract and structure the response strategy components."""
        strategy: Dict[str, List[str]] = {
            "initial_response": [],
            "talking_points": [],
            "supporting_evidence": [],
            "discovery_questions": [],
            "alternative_approaches": []
        }
        
        current_section = None
        
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            lower_line = line.lower()
            if "initial" in lower_line or "response" in lower_line:
                current_section = "initial_response"
            elif "talking" in lower_line or "points" in lower_line:
                current_section = "talking_points"
            elif "evidence" in lower_line or "support" in lower_line:
                current_section = "supporting_evidence"
            elif "question" in lower_line or "discovery" in lower_line:
                current_section = "discovery_questions"
            elif "alternative" in lower_line or "approach" in lower_line:
                current_section = "alternative_approaches"
            elif current_section and line.startswith("-"):
                strategy[current_section].append(line[1:].strip())
            elif current_section and line:
                strategy[current_section].append(line)
        
        return strategy

    async def generate_objection_library(
        self,
        product_info: Dict[str, Any],
        competitor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive library of potential objections and responses."""
        system_prompt = """
        Based on the product and competitor information provided, generate
        a comprehensive library of potential sales objections and effective
        responses. Focus on common objection categories:
        1. Price/Budget
        2. Product Features
        3. Competition
        4. Implementation/Integration
        5. Timing/Urgency
        6. Authority/Decision Making
        """
        
        analysis_prompt = f"""
        Product Information:
        {json.dumps(product_info, indent=2)}

        Competitor Information:
        {json.dumps(competitor_info, indent=2)}

        Please generate a structured library of objections and responses.
        """
        
        raw_analysis = await self._call_claude(
            prompt=analysis_prompt,
            system=system_prompt,
            max_tokens=3000
        )
        
        try:
            return json.loads(raw_analysis)
        except json.JSONDecodeError:
            return {
                "objection_library": self._extract_response_strategy(raw_analysis)
            } 