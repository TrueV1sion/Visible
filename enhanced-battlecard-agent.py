from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
import anthropic
import openai
from .base_agent import BaseAgent
from .prompt_management import PromptLibrary, PromptManager, PromptType


class EnhancedBattlecardGenerationAgent(BaseAgent):
    """Enhanced agent for generating comprehensive battlecards with advanced AI."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the enhanced battlecard generation agent.
        
        Args:
            config: Configuration dictionary containing generation parameters
        """
        super().__init__(config)
        self.config = config or {}
        
        # Initialize prompt library and manager
        self.prompt_library = PromptLibrary(self.config.get('prompts_path', 'data/prompts'))
        self.prompt_manager = PromptManager(self.prompt_library)
        
        # Initialize AI clients
        self.anthropic_client = self._init_anthropic_client()
        self.openai_client = self._init_openai_client()
        
        # Configure sections to generate
        self.sections = self.config.get('sections', [
            'overview',
            'competitive_analysis',
            'strengths_weaknesses',
            'pricing_comparison',
            'objection_handling',
            'winning_strategies'
        ])
        
        # Configure complexity levels
        self.complexity_levels = {
            'overview': 'medium_complexity',
            'competitive_analysis': 'high_complexity',
            'strengths_weaknesses': 'medium_complexity',
            'pricing_comparison': 'medium_complexity',
            'objection_handling': 'high_complexity',
            'winning_strategies': 'high_complexity'
        }
        
        # Map sections to prompt types
        self.section_to_prompt_type = {
            'overview': PromptType.BATTLECARD_OVERVIEW,
            'competitive_analysis': PromptType.COMPETITIVE_ANALYSIS,
            'strengths_weaknesses': PromptType.STRENGTHS_WEAKNESSES,
            'pricing_comparison': PromptType.PRICING_COMPARISON,
            'objection_handling': PromptType.OBJECTION_HANDLING,
            'winning_strategies': PromptType.WINNING_STRATEGIES,
        }

    def _init_anthropic_client(self) -> Optional[anthropic.Anthropic]:
        """Initialize the Anthropic client."""
        api_key = self.config.get('anthropic_api_key')
        if not api_key:
            self.logger.warning("No Anthropic API key provided. Some features may be limited.")
            return None
        
        return anthropic.Anthropic(api_key=api_key)
    
    def _init_openai_client(self) -> Optional[openai.OpenAI]:
        """Initialize the OpenAI client."""
        api_key = self.config.get('openai_api_key')
        if not api_key:
            self.logger.warning("No OpenAI API key provided. Some features may be limited.")
            return None
        
        return openai.AsyncOpenAI(api_key=api_key)
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing data for battlecard
            
        Returns:
            Boolean indicating if input is valid
        """
        required_fields = [
            'competitor_info',
            'product_analysis',
            'insights',
            'market_data'
        ]
        return all(field in input_data for field in required_fields)
    
    async def generate_section(
        self, 
        section_name: str, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a specific section of the battlecard.
        
        Args:
            section_name: Name of the section to generate
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing generated section
        """
        prompt_type = self.section_to_prompt_type.get(section_name)
        if not prompt_type:
            self.logger.warning(f"No prompt type defined for section {section_name}")
            return {"error": f"No prompt type defined for section {section_name}"}
        
        # Get appropriate templates
        templates = self.prompt_library.list_templates(prompt_type)
        if not templates:
            self.logger.warning(f"No templates found for prompt type {prompt_type}")
            return {"error": f"No templates found for section {section_name}"}
        
        # Select the first available template
        template = templates[0]
        
        # Prepare variables for the template
        variables = self._prepare_variables_for_section(section_name, input_data)
        
        # Determine complexity level
        complexity = self.complexity_levels.get(section_name, "medium_complexity")
        
        # Generate content using the prompt manager
        result = await self.prompt_manager.generate_content(
            template.template_id,
            variables,
            task_complexity=complexity,
            anthropic_client=self.anthropic_client,
            openai_client=self.openai_client
        )
        
        if result['status'] != 'success':
            self.logger.error(f"Error generating {section_name}: {result.get('message', 'Unknown error')}")
            return {"error": f"Failed to generate {section_name}"}
        
        # Process and structure the response based on section type
        structured_content = self._structure_section_content(section_name, result['content'])
        
        return {
            "content": structured_content,
            "raw_content": result['content'],
            "model_used": result['model'],
            "metrics": result['metrics']
        }
    
    def _prepare_variables_for_section(
        self, 
        section_name: str, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare variables for a specific section template.
        
        Args:
            section_name: Name of the section to generate
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary of variables for the template
        """
        competitor_info = input_data['competitor_info']
        product_analysis = input_data['product_analysis']
        insights = input_data['insights']
        market_data = input_data['market_data']
        
        # Common variables
        variables = {
            "competitor_name": competitor_info.get('name', 'Unknown Competitor'),
            "our_product_name": self.config.get('product_name', 'Our Product')
        }
        
        # Section-specific variables
        if section_name == 'overview':
            variables.update({
                "competitor_context": json.dumps(competitor_info, indent=2),
                "market_context": json.dumps(market_data, indent=2)
            })
        
        elif section_name == 'competitive_analysis':
            variables.update({
                "competitor_features": json.dumps(product_analysis.get('competitive_analysis', {}), indent=2),
                "our_product_features": json.dumps(product_analysis.get('common_features', {}), indent=2),
                "market_positioning": json.dumps(product_analysis.get('market_positioning', {}), indent=2)
            })
        
        elif section_name == 'strengths_weaknesses':
            variables.update({
                "competitor_features": json.dumps(competitor_info.get('features', []), indent=2),
                "our_product_features": json.dumps(self.config.get('our_features', []), indent=2),
                "competitive_landscape": json.dumps(insights.get('competitive_landscape', {}), indent=2)
            })
        
        elif section_name == 'pricing_comparison':
            variables.update({
                "our_pricing": json.dumps(self.config.get('our_pricing', {}), indent=2),
                "competitor_pricing": json.dumps(competitor_info.get('pricing', {}), indent=2),
                "pricing_analysis": json.dumps(insights.get('pricing_analysis', {}), indent=2)
            })
        
        elif section_name == 'objection_handling':
            variables.update({
                "competitor_details": json.dumps(competitor_info, indent=2),
                "our_product_details": json.dumps(self.config.get('our_product_details', {}), indent=2),
                "common_objections": json.dumps(insights.get('objections', []), indent=2)
            })
        
        elif section_name == 'winning_strategies':
            variables.update({
                "competitor_details": json.dumps(competitor_info, indent=2),
                "our_solution_advantages": json.dumps(insights.get('recommendations', []), indent=2),
                "market_trends": json.dumps(insights.get('trends', []), indent=2)
            })
        
        return variables
    
    def _structure_section_content(self, section_name: str, content: str) -> Dict[str, Any]:
        """
        Structure the raw content into a structured format based on section type.
        
        Args:
            section_name: Name of the section
            content: Raw content from AI
            
        Returns:
            Dictionary with structured content
        """
        # For simplicity, we'll return a basic structure
        # In a production environment, this would parse the AI response into
        # a structured format appropriate for each section type
        
        if section_name == 'overview':
            # Extract key parts from the overview
            lines = content.split('\n')
            structured = {
                'company_name': '',
                'description': '',
                'key_metrics': {},
                'target_market': [],
                'recent_developments': []
            }
            
            current_section = 'description'
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "company" in line.lower() and ":" in line:
                    structured['company_name'] = line.split(':', 1)[1].strip()
                elif "target market" in line.lower() or "ideal customer" in line.lower():
                    current_section = 'target_market'
                    if ":" in line:
                        target = line.split(':', 1)[1].strip()
                        if target:
                            structured['target_market'].append(target)
                elif "development" in line.lower() or "recent" in line.lower():
                    current_section = 'recent_developments'
                    if ":" in line:
                        dev = line.split(':', 1)[1].strip()
                        if dev:
                            structured['recent_developments'].append(dev)
                elif line.startswith("- ") or line.startswith("* "):
                    item = line[2:].strip()
                    if current_section == 'target_market':
                        structured['target_market'].append(item)
                    elif current_section == 'recent_developments':
                        structured['recent_developments'].append(item)
                    else:
                        # Add to description if not in a specific list
                        structured['description'] += f"\n{line}"
                else:
                    structured['description'] += f"\n{line}"
            
            # Clean up the description
            structured['description'] = structured['description'].strip()
            
            return structured
        
        elif section_name == 'strengths_weaknesses':
            # Split into strengths, weaknesses, opportunities, threats
            structured = {
                'strengths': [],
                'weaknesses': [],
                'opportunities': [],
                'threats': []
            }
            
            current_section = None
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if "strength" in line.lower():
                    current_section = 'strengths'
                    continue
                elif "weakness" in line.lower():
                    current_section = 'weaknesses'
                    continue
                elif "opportunit" in line.lower():
                    current_section = 'opportunities'
                    continue
                elif "threat" in line.lower():
                    current_section = 'threats'
                    continue
                
                if current_section and (line.startswith("- ") or line.startswith("* ")):
                    item = line[2:].strip()
                    structured[current_section].append(item)
            
            return structured
        
        elif section_name == 'objection_handling':
            # Parse objections and responses
            objections = []
            current_objection = None
            current_response = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    if current_objection and current_response:
                        objections.append({
                            'objection': current_objection,
                            'response': '\n'.join(current_response),
                            'evidence': []  # Would need more complex parsing for evidence
                        })
                        current_objection = None
                        current_response = []
                    continue
                
                if line.startswith('"') or line.startswith('"') or line.startswith("Objection:"):
                    # If we already have an objection in progress, save it
                    if current_objection and current_response:
                        objections.append({
                            'objection': current_objection,
                            'response': '\n'.join(current_response),
                            'evidence': []
                        })
                        current_response = []
                    
                    # Extract the new objection
                    current_objection = line.replace('Objection:', '').replace('"', '').replace('"', '').strip()
                
                elif line.startswith("Response:") or line.startswith("a)") or current_objection and not current_response:
                    # Start of a response
                    response_text = line
                    if line.startswith("Response:"):
                        response_text = line[9:].strip()
                    elif line.startswith("a)"):
                        response_text = line[2:].strip()
                    
                    if response_text:
                        current_response.append(response_text)
                
                elif current_objection and current_response:
                    current_response.append(line)
            
            # Add the last objection if needed
            if current_objection and current_response:
                objections.append({
                    'objection': current_objection,
                    'response': '\n'.join(current_response),
                    'evidence': []
                })
            
            return {'objections': objections}
        
        elif section_name == 'winning_strategies':
            # Extract strategies
            strategies = []
            current_strategy = None
            current_details = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    if current_strategy and current_details:
                        strategies.append({
                            'focus_area': current_strategy,
                            'strategy': current_strategy,
                            'details': current_details,
                            'priority': 'Medium'  # Default priority
                        })
                        current_strategy = None
                        current_details = []
                    continue
                
                if line.endswith(":") or (line.startswith("#") and ":" in line):
                    # If we already have a strategy in progress, save it
                    if current_strategy and current_details:
                        strategies.append({
                            'focus_area': current_strategy,
                            'strategy': current_strategy,
                            'details': current_details,
                            'priority': 'Medium'
                        })
                        current_details = []
                    
                    # Extract the new strategy
                    current_strategy = line.replace('#', '').replace(':', '').strip()
                
                elif line.startswith("- ") or line.startswith("* "):
                    if current_strategy:
                        current_details.append(line[2:].strip())
                
                elif current_strategy and not line.startswith("#"):
                    # Could be details text not in bullet form
                    current_details.append(line)
            
            # Add the last strategy if needed
            if current_strategy and current_details:
                strategies.append({
                    'focus_area': current_strategy,
                    'strategy': current_strategy,
                    'details': current_details,
                    'priority': 'Medium'
                })
            
            return {'strategies': strategies}
        
        # Default handling for sections without specific structure
        return {'content': content}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data and generate battlecard.
        
        Args:
            input_data: Dictionary containing data for battlecard
            
        Returns:
            Dictionary containing generated battlecard
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            battlecard = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'competitor': input_data['competitor_info'].get('name')
                }
            }
            
            # Generate each section in parallel
            section_tasks = {
                section: asyncio.create_task(self.generate_section(section, input_data))
                for section in self.sections
            }
            
            # Wait for all tasks to complete
            completed_sections = {}
            for section, task in section_tasks.items():
                try:
                    result = await task
                    if 'error' not in result:
                        completed_sections[section] = result['content']
                    else:
                        self.logger.error(f"Error generating section {section}: {result['error']}")
                        completed_sections[section] = {'error': result['error']}
                except Exception as e:
                    self.logger.error(f"Exception in section {section}: {str(e)}")
                    completed_sections[section] = {'error': str(e)}
            
            # Add all sections to the battlecard
            battlecard.update(completed_sections)
            
            return {
                'status': 'success',
                'data': battlecard,
                'metadata': {
                    'sections_generated': list(completed_sections.keys()),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating battlecard: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def get_template_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for all templates.
        
        Returns:
            Dictionary containing template usage stats
        """
        stats = {}
        for template in self.prompt_library.list_templates():
            stats[template.template_id] = {
                'name': template.name,
                'type': template.type,
                'usage_count': template.usage_count,
                'last_used': template.last_used.isoformat() if template.last_used else None,
                'versions': len(template.versions)
            }
        
        return stats
    
    def create_or_update_template(
        self,
        template_type: PromptType,
        name: str,
        content: str,
        variables: List[str],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new template or update an existing one.
        
        Args:
            template_type: Type of the template
            name: Name of the template
            content: Prompt content
            variables: List of variable names
            description: Template description
            tags: List of tags
            
        Returns:
            Dictionary with template information
        """
        # Check if template exists
        existing = [
            t for t in self.prompt_library.list_templates() 
            if t.name == name and t.type == template_type
        ]
        
        if existing:
            # Update existing template
            template = existing[0]
            version_id = self.prompt_library.add_version(
                template.template_id,
                content,
                description=f"Updated on {datetime.now().isoformat()}",
                set_active=True
            )
            
            return {
                'status': 'updated',
                'template_id': template.template_id,
                'version_id': version_id
            }
        else:
            # Create new template
            template = self.prompt_library.create_template(
                name=name,
                prompt_type=template_type,
                content=content,
                variables=variables,
                description=description,
                tags=tags
            )
            
            return {
                'status': 'created',
                'template_id': template.template_id,
                'version_id': template.active_version_id
            }


# Example usage code
async def example_usage():
    # Create configuration
    config = {
        'anthropic_api_key': 'your_anthropic_api_key',
        'openai_api_key': 'your_openai_api_key',
        'product_name': 'ProductX',
        'sections': [
            'overview',
            'strengths_weaknesses',
            'objection_handling',
            'winning_strategies'
        ],
        'our_features': [
            'API integration',
            'SSO',
            'Data encryption',
            'Custom reports'
        ],
        'our_pricing': {
            'starter': '$10/month',
            'professional': '$50/month',
            'enterprise': '$200/month'
        }
    }
    
    # Initialize the agent
    agent = EnhancedBattlecardGenerationAgent(config)
    
    # Prepare input data
    input_data = {
        'competitor_info': {
            'name': 'CompetitorY',
            'description': 'Cloud-based solution provider',
            'market_share': '15%',
            'features': [
                'Basic reporting',
                'Email integration',
                'SSO'
            ],
            'pricing': {
                'basic': '$15/month',
                'business': '$75/month'
            }
        },
        'product_analysis': {
            'competitive_analysis': {
                'advantages': ['Better security', 'More integrations'],
                'disadvantages': ['Higher price point']
            },
            'common_features': {
                'Security': ['encryption', 'authentication'],
                'Integration': ['API', 'webhooks']
            },
            'market_positioning': [
                {'name': 'ProductX', 'uniqueness_score': 0.8},
                {'name': 'CompetitorY', 'uniqueness_score': 0.6}
            ]
        },
        'insights': {
            'competitive_landscape': {
                'position_analysis': {
                    'key_advantages': ['Market leader', 'Strong brand'],
                    'key_disadvantages': ['Higher pricing', 'Complex setup']
                }
            },
            'recommendations': [
                {
                    'category': 'Product Improvement',
                    'priority': 'High',
                    'recommendation': 'Simplify setup process',
                    'details': ['Reduce time to value'],
                    'impact': 'Customer satisfaction'
                }
            ],
            'trends': [
                {
                    'topic': 'cloud adoption',
                    'keywords': ['cloud', 'migration', 'digital'],
                    'document_count': 3,
                    'example_text': 'Growing cloud adoption trend'
                }
            ]
        },
        'market_data': {
            'market_size': 1000000,
            'growth_rate': 0.15
        }
    }
    
    # Generate battlecard
    result = await agent.process(input_data)
    
    # Print the result
    if result['status'] == 'success':
        print(f"Successfully generated battlecard for {result['data']['metadata']['competitor']}")
        print(f"Sections: {result['metadata']['sections_generated']}")
        
        # Example of accessing a specific section
        if 'overview' in result['data']:
            print("\nOVERVIEW:")
            overview = result['data']['overview']
            print(f"Description: {overview.get('description', 'N/A')}")
            print(f"Target Market: {', '.join(overview.get('target_market', ['N/A']))}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Get template usage stats
    stats = agent.get_template_usage_stats()
    print("\nTemplate Usage Statistics:")
    for template_id, stat in stats.items():
        print(f"- {stat['name']} ({stat['type']}): Used {stat['usage_count']} times")


if __name__ == "__main__":
    asyncio.run(example_usage())