from typing import Any, Dict, List
import json
from datetime import datetime
from ..base import BaseAgent


class UseCaseGenerationAgent(BaseAgent):
    """Agent for generating and analyzing customer use cases."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process customer data and generate structured use cases."""
        if not self._validate_input(input_data):
            raise ValueError("Invalid input data format")

        # Prepare system prompt
        system_prompt = """
        You are an expert in analyzing customer success stories and creating
        compelling use cases. Your task is to transform customer data into
        structured, persuasive case studies that highlight value creation
        and successful outcomes.
        
        For each use case, provide:
        1. Customer profile and industry context
        2. Business challenges and pain points
        3. Solution implementation details
        4. Measurable outcomes and ROI
        5. Key success factors and lessons learned
        """

        # Prepare use case analysis prompt
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
        """Validate that input contains required use case data."""
        required_fields = ["customer_data", "solution_details"]
        return all(field in input_data for field in required_fields)

    def _prepare_analysis_prompt(self, input_data: Dict[str, Any]) -> str:
        """Prepare the analysis prompt based on customer data."""
        customer_data = input_data["customer_data"]
        solution_details = input_data["solution_details"]
        outcomes = input_data.get("outcomes", {})
        
        prompt = f"""
        Generate a detailed use case analysis based on the following:

        Customer Information:
        {json.dumps(customer_data, indent=2)}

        Solution Implementation:
        {json.dumps(solution_details, indent=2)}

        Outcomes and Metrics:
        {json.dumps(outcomes, indent=2) if outcomes else "No outcome data provided"}

        Please provide a structured analysis covering:
        1. Customer Profile
        2. Business Challenges
        3. Solution Overview
        4. Implementation Process
        5. Results and Benefits
        6. Success Factors
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
                "use_case": self._extract_use_case_sections(raw_output),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _extract_use_case_sections(self, text: str) -> Dict[str, List[str]]:
        """Extract and structure different sections of the use case."""
        sections: Dict[str, List[str]] = {
            "customer_profile": [],
            "business_challenges": [],
            "solution_overview": [],
            "implementation": [],
            "results": [],
            "success_factors": []
        }
        
        current_section = None
        
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            lower_line = line.lower()
            if "profile" in lower_line or "customer" in lower_line:
                current_section = "customer_profile"
            elif "challenge" in lower_line or "problem" in lower_line:
                current_section = "business_challenges"
            elif "solution" in lower_line or "overview" in lower_line:
                current_section = "solution_overview"
            elif "implement" in lower_line or "process" in lower_line:
                current_section = "implementation"
            elif "result" in lower_line or "benefit" in lower_line:
                current_section = "results"
            elif "success" in lower_line or "factor" in lower_line:
                current_section = "success_factors"
            elif current_section and line.startswith("-"):
                sections[current_section].append(line[1:].strip())
            elif current_section and line:
                sections[current_section].append(line)
        
        return sections

    async def identify_patterns(
        self,
        use_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze multiple use cases to identify common patterns and insights."""
        system_prompt = """
        Analyze the provided collection of use cases to identify:
        1. Common success patterns
        2. Industry-specific trends
        3. Key value drivers
        4. Implementation best practices
        5. ROI patterns and metrics
        """
        
        analysis_prompt = f"""
        Use Cases:
        {json.dumps(use_cases, indent=2)}

        Please provide a comprehensive analysis of patterns and insights.
        """
        
        raw_analysis = await self._call_claude(
            prompt=analysis_prompt,
            system=system_prompt,
            max_tokens=2000
        )
        
        try:
            return json.loads(raw_analysis)
        except json.JSONDecodeError:
            return {
                "patterns": self._extract_use_case_sections(raw_analysis),
                "analyzed_at": datetime.utcnow().isoformat()
            } 