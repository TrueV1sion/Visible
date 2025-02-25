from typing import Dict, Any, List, Optional, Union
import json
import os
import yaml
from datetime import datetime
from pydantic import BaseModel, Field
import hashlib
import asyncio
from enum import Enum


class PromptType(str, Enum):
    BATTLECARD_OVERVIEW = "battlecard_overview"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    OBJECTION_HANDLING = "objection_handling"
    PRICING_COMPARISON = "pricing_comparison"
    STRENGTHS_WEAKNESSES = "strengths_weaknesses"
    WINNING_STRATEGIES = "winning_strategies"
    CUSTOM = "custom"


class PromptVersion(BaseModel):
    version_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    description: Optional[str] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)


class PromptTemplate(BaseModel):
    template_id: str
    type: PromptType
    name: str
    description: Optional[str] = None
    active_version_id: str
    versions: Dict[str, PromptVersion] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    usage_count: int = 0
    last_used: Optional[datetime] = None


class PromptLibrary:
    def __init__(self, storage_path: str = "data/prompts"):
        self.storage_path = storage_path
        self.templates: Dict[str, PromptTemplate] = {}
        self._ensure_storage_path()
        self._load_templates()
    
    def _ensure_storage_path(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_templates(self) -> None:
        """Load all templates from storage."""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        data = json.load(f)
                        template = PromptTemplate(**data)
                        self.templates[template.template_id] = template
                except Exception as e:
                    print(f"Error loading template {filename}: {str(e)}")
    
    def save_template(self, template: PromptTemplate) -> None:
        """Save a template to storage."""
        template_path = os.path.join(self.storage_path, f"{template.template_id}.json")
        with open(template_path, 'w') as f:
            f.write(template.model_dump_json(indent=2))
        self.templates[template.template_id] = template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, prompt_type: Optional[PromptType] = None) -> List[PromptTemplate]:
        """List all templates, optionally filtered by type."""
        if prompt_type:
            return [t for t in self.templates.values() if t.type == prompt_type]
        return list(self.templates.values())
    
    def create_template(
        self,
        name: str,
        prompt_type: PromptType,
        content: str,
        variables: List[str],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> PromptTemplate:
        """Create a new prompt template."""
        # Generate a template ID
        template_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Create the initial version
        version_id = f"v1_{datetime.now().strftime('%Y%m%d')}"
        version = PromptVersion(
            version_id=version_id,
            content=content,
            description=f"Initial version"
        )
        
        # Create the template
        template = PromptTemplate(
            template_id=template_id,
            type=prompt_type,
            name=name,
            description=description,
            active_version_id=version_id,
            versions={version_id: version},
            variables=variables,
            tags=tags or []
        )
        
        # Save and return
        self.save_template(template)
        return template
    
    def add_version(
        self,
        template_id: str,
        content: str,
        description: Optional[str] = None,
        set_active: bool = True,
        created_by: Optional[str] = None
    ) -> Optional[str]:
        """Add a new version to an existing template."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Generate version ID
        version_count = len(template.versions) + 1
        version_id = f"v{version_count}_{datetime.now().strftime('%Y%m%d')}"
        
        # Create version
        version = PromptVersion(
            version_id=version_id,
            content=content,
            description=description,
            created_by=created_by
        )
        
        # Update template
        template.versions[version_id] = version
        if set_active:
            template.active_version_id = version_id
        
        # Save updates
        self.save_template(template)
        return version_id
    
    def set_active_version(self, template_id: str, version_id: str) -> bool:
        """Set the active version for a template."""
        template = self.get_template(template_id)
        if not template or version_id not in template.versions:
            return False
        
        template.active_version_id = version_id
        self.save_template(template)
        return True
    
    def get_prompt_content(self, template_id: str, version_id: Optional[str] = None) -> Optional[str]:
        """Get the content for a specific prompt version."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        version_id = version_id or template.active_version_id
        version = template.versions.get(version_id)
        if not version:
            return None
        
        return version.content
    
    def update_metrics(self, template_id: str, version_id: str, metrics: Dict[str, float]) -> bool:
        """Update performance metrics for a prompt version."""
        template = self.get_template(template_id)
        if not template or version_id not in template.versions:
            return False
        
        version = template.versions[version_id]
        version.performance_metrics.update(metrics)
        template.usage_count += 1
        template.last_used = datetime.now()
        
        self.save_template(template)
        return True
    
    def render_prompt(self, template_id: str, variables: Dict[str, Any], version_id: Optional[str] = None) -> Optional[str]:
        """Render a prompt with variables."""
        content = self.get_prompt_content(template_id, version_id)
        if not content:
            return None
        
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Basic variable substitution
        for var in template.variables:
            if var in variables:
                placeholder = f"{{{var}}}"
                value = str(variables[var])
                content = content.replace(placeholder, value)
        
        return content


class PromptManager:
    def __init__(self, library: PromptLibrary, default_model: str = "claude-3-sonnet-20240229"):
        self.library = library
        self.default_model = default_model
        self.model_mapping = {
            "low_complexity": "claude-3-haiku-20240307",
            "medium_complexity": "claude-3-sonnet-20240229",
            "high_complexity": "claude-3-opus-20240229"
        }
    
    def get_model_for_task(self, task_complexity: str) -> str:
        """Get the appropriate model for a task complexity level."""
        return self.model_mapping.get(task_complexity, self.default_model)
    
    async def generate_content(
        self,
        template_id: str,
        variables: Dict[str, Any],
        task_complexity: str = "medium_complexity",
        version_id: Optional[str] = None,
        anthropic_client=None,
        openai_client=None
    ) -> Dict[str, Any]:
        """Generate content using a prompt template and AI model."""
        # Get the rendered prompt
        prompt = self.library.render_prompt(template_id, variables, version_id)
        if not prompt:
            return {"status": "error", "message": "Prompt template not found"}
        
        # Get the template for metrics tracking
        template = self.library.get_template(template_id)
        version_id = version_id or template.active_version_id if template else None
        
        # Select the model based on task complexity
        model = self.get_model_for_task(task_complexity)
        
        try:
            # Call the appropriate AI model
            if "claude" in model and anthropic_client:
                start_time = datetime.now()
                response = await anthropic_client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                duration = (datetime.now() - start_time).total_seconds()
                content = response.content[0].text
            elif openai_client:
                start_time = datetime.now()
                response = await openai_client.chat.completions.create(
                    model="gpt-4-turbo",  # Use appropriate OpenAI model
                    messages=[
                        {"role": "system", "content": "You are a competitive intelligence expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000
                )
                duration = (datetime.now() - start_time).total_seconds()
                content = response.choices[0].message.content
            else:
                return {"status": "error", "message": "No AI client available"}
            
            # Update metrics
            if template and version_id:
                self.library.update_metrics(template.template_id, version_id, {
                    "response_time": duration,
                    "token_count": len(content.split())
                })
            
            return {
                "status": "success",
                "content": content,
                "model": model,
                "metrics": {
                    "response_time": duration,
                    "token_count": len(content.split())
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


class PromptABTesting:
    def __init__(self, library: PromptLibrary, test_id: str, template_variants: List[str]):
        self.library = library
        self.test_id = test_id
        self.template_variants = template_variants
        self.results: Dict[str, List[Dict[str, float]]] = {variant: [] for variant in template_variants}
    
    def record_result(self, variant_id: str, metrics: Dict[str, float]) -> None:
        """Record performance metrics for a variant."""
        if variant_id in self.results:
            self.results[variant_id].append(metrics)
    
    def get_best_variant(self, metric_key: str = "quality_score") -> str:
        """Get the best performing variant based on a specific metric."""
        averages = {}
        for variant_id, metrics_list in self.results.items():
            if metrics_list:
                avg = sum(m.get(metric_key, 0) for m in metrics_list) / len(metrics_list)
                averages[variant_id] = avg
        
        if not averages:
            return self.template_variants[0] if self.template_variants else ""
        
        return max(averages.items(), key=lambda x: x[1])[0]
    
    def save_results(self, path: str) -> None:
        """Save test results to a file."""
        with open(path, 'w') as f:
            json.dump({
                "test_id": self.test_id,
                "template_variants": self.template_variants,
                "results": self.results
            }, f, indent=2)


# Initialize default templates
def create_default_templates(library: PromptLibrary) -> None:
    """Create default prompt templates if they don't exist."""
    default_templates = [
        {
            "name": "Battlecard Overview",
            "type": PromptType.BATTLECARD_OVERVIEW,
            "content": """
You are an expert competitive intelligence analyst. Create a comprehensive overview for a battlecard about {competitor_name}.

Include the following information:
1. Company background and history
2. Key metrics (founded, revenue if public, employees, funding)
3. Target market and ideal customer profile
4. Core value proposition and positioning
5. Notable recent developments (last 6-12 months)

Use the following additional context:
{competitor_context}

Format the overview as a concise, factual summary that a sales professional can quickly read to understand the competitor. Use bullet points where appropriate.
            """,
            "variables": ["competitor_name", "competitor_context"],
            "description": "Generates a comprehensive overview of a competitor for battlecards",
            "tags": ["overview", "competitor", "battlecard"]
        },
        {
            "name": "Strengths and Weaknesses Analysis",
            "type": PromptType.STRENGTHS_WEAKNESSES,
            "content": """
As a competitive intelligence expert, analyze the strengths and weaknesses of {competitor_name} compared to our product {our_product_name}.

Product Context:
{competitor_features}

Our Product Features:
{our_product_features}

Please create a detailed SWOT analysis with:

1. Competitor's Key Strengths (minimum 3):
   * Focus on their unique advantages
   * Include specific features or capabilities that set them apart
   * Highlight market perception strengths

2. Competitor's Key Weaknesses (minimum 3):
   * Identify gaps in their offering
   * Note any implementation, support, or infrastructure limitations
   * Include pricing or business model weaknesses if applicable

3. Our Competitive Opportunities:
   * Where we can capitalize on their weaknesses
   * Market segments they underserve
   * Emerging needs they aren't addressing

4. Competitive Threats:
   * How their strengths threaten our position
   * Potential future developments to watch for
   * Market shifts that could favor their approach

Format this for sales professionals to quickly understand the competitive landscape.
            """,
            "variables": ["competitor_name", "our_product_name", "competitor_features", "our_product_features"],
            "description": "Analyzes strengths and weaknesses of a competitor compared to our product",
            "tags": ["SWOT", "analysis", "battlecard"]
        },
        {
            "name": "Objection Handling Guide",
            "type": PromptType.OBJECTION_HANDLING,
            "content": """
You are a competitive intelligence and sales enablement expert. Create a comprehensive objection handling guide for sales conversations when competing against {competitor_name}.

Based on the following competitor information:
{competitor_details}

And our product information:
{our_product_details}

Generate strategic responses for these common objections:

1. "{competitor_name} is cheaper than your solution"
2. "{competitor_name} has more features than your product"
3. "{competitor_name} has better market reputation/reviews"
4. "{competitor_name} integrates better with our existing systems"
5. "We're already using {competitor_name} and switching would be difficult"

For each objection, provide:
a) A concise, non-defensive acknowledgment
b) 2-3 key talking points that highlight our advantages
c) A specific customer success story or metric that supports our position
d) A thoughtful question to shift the conversation forward

The responses should be:
- Factual and honest (never disparaging the competitor)
- Focused on customer value rather than feature comparisons
- Concise and easy for sales reps to internalize
- Backed by specific evidence where possible
            """,
            "variables": ["competitor_name", "competitor_details", "our_product_details"],
            "description": "Generates responses to common competitive objections",
            "tags": ["objections", "sales", "battlecard"]
        },
        {
            "name": "Pricing Comparison",
            "type": PromptType.PRICING_COMPARISON,
            "content": """
You are a pricing analyst specializing in competitive intelligence. Create a detailed pricing comparison between our product and {competitor_name}.

Our Pricing Information:
{our_pricing}

Competitor Pricing Information:
{competitor_pricing}

Please analyze and provide:

1. Side-by-side tier comparison
   * Match equivalent tiers where possible
   * Highlight key differences in what's included

2. TCO Analysis (Total Cost of Ownership)
   * Include implementation costs
   * Maintenance and support fees
   * Required add-ons or modules
   * Typical discount structures

3. Value Analysis
   * Price-to-value ratio comparison
   * Where we provide better value
   * Where they might appear more cost-effective

4. Pricing Strategy Insights
   * Hidden costs or fee structures
   * Contract terms that impact total cost
   * Negotiation leverage points

5. Talking Points for Sales
   * How to position our pricing as an advantage
   * How to address when their pricing appears lower
   * ROI arguments that justify our pricing

Format this as a clear, factual analysis that helps sales teams navigate pricing discussions confidently.
            """,
            "variables": ["competitor_name", "our_pricing", "competitor_pricing"],
            "description": "Provides detailed pricing comparison between our product and a competitor",
            "tags": ["pricing", "comparison", "battlecard"]
        },
        {
            "name": "Winning Strategies",
            "type": PromptType.WINNING_STRATEGIES,
            "content": """
You are a sales strategy consultant specializing in competitive deals. Create a practical guide for winning against {competitor_name} in competitive sales situations.

Competitor Context:
{competitor_details}

Our Solution Advantages:
{our_solution_advantages}

Based on this information, develop:

1. Strategic Win Themes (3-5)
   * Key differentiation points to emphasize throughout the sales cycle
   * Value narrative that positions us as the superior choice

2. Qualification Strategies
   * Questions to ask to identify if this prospect is a good fit
   * Early indicators that we can win against this competitor

3. Competitive Displacement Tactics
   * For existing {competitor_name} customers
   * Migration path and value story

4. Pre-emptive Strategies
   * How to position against {competitor_name} before they're mentioned
   * Setting evaluation criteria that favor our strengths

5. Late-Stage Competition Tactics
   * Approaches when discovered late in the sales cycle
   * Techniques to restart the evaluation process

6. Decision-Maker Engagement
   * Strategies to reach and influence senior decision-makers
   * Value discussions that resonate at executive levels

Format this as actionable advice that sales representatives can immediately apply to competitive deals. Include specific examples, questions to ask, and talking points where possible.
            """,
            "variables": ["competitor_name", "competitor_details", "our_solution_advantages"],
            "description": "Provides strategies for winning against a specific competitor",
            "tags": ["strategy", "sales", "battlecard", "competitive"]
        }
    ]
    
    for template_data in default_templates:
        # Check if template already exists by name/type
        existing = [t for t in library.list_templates() if t.name == template_data["name"] and t.type == template_data["type"]]
        if not existing:
            library.create_template(
                name=template_data["name"],
                prompt_type=template_data["type"],
                content=template_data["content"],
                variables=template_data["variables"],
                description=template_data["description"],
                tags=template_data["tags"]
            )


# Example usage
async def main():
    # Initialize the prompt library
    library = PromptLibrary("data/prompts")
    
    # Create default templates if none exist
    if not library.list_templates():
        create_default_templates(library)
    
    # Initialize the prompt manager
    manager = PromptManager(library)
    
    # Example: Generate content using a template
    variables = {
        "competitor_name": "Acme Corp",
        "competitor_context": "Acme Corp is a leading provider of cloud solutions founded in 2010. They raised $50M in Series C funding last year and have approximately 500 employees. Their primary target market is mid-sized enterprises."
    }
    
    # Get list of templates
    templates = library.list_templates()
    if templates:
        # Use the first template
        template = templates[0]
        print(f"Using template: {template.name}")
        
        # Generate content (in a real app, you'd pass the actual clients)
        result = await manager.generate_content(
            template.template_id,
            variables,
            anthropic_client=None,  # Pass your anthropic client here
            openai_client=None  # Pass your openai client here
        )
        
        print(f"Generation status: {result['status']}")
        if result['status'] == 'success':
            print(f"Generated content:\n{result['content']}")


if __name__ == "__main__":
    asyncio.run(main())
