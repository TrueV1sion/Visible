from typing import Dict, Any, List
from datetime import datetime
import json
from .base_agent import BaseAgent


class BattlecardGenerationAgent(BaseAgent):
    """Agent for generating comprehensive battlecards."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the battlecard generation agent.
        
        Args:
            config: Configuration dictionary containing generation parameters
        """
        super().__init__(config)
        self.config = config or {}
        self.template = self.config.get('template', 'standard')
        self.sections = self.config.get('sections', [
            'overview',
            'competitive_analysis',
            'strengths_weaknesses',
            'pricing_comparison',
            'objection_handling',
            'winning_strategies'
        ])

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

    def generate_overview(
        self,
        competitor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate competitor overview section.
        
        Args:
            competitor_info: Dictionary containing competitor information
            
        Returns:
            Dictionary containing overview section
        """
        return {
            'company_name': competitor_info.get('name', ''),
            'description': competitor_info.get('description', ''),
            'key_metrics': {
                'market_share': competitor_info.get('market_share', 'N/A'),
                'revenue': competitor_info.get('revenue', 'N/A'),
                'growth_rate': competitor_info.get('growth_rate', 'N/A')
            },
            'target_market': competitor_info.get('target_market', []),
            'key_customers': competitor_info.get('key_customers', [])[:5]
        }

    def generate_competitive_analysis(
        self,
        product_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate competitive analysis section.
        
        Args:
            product_analysis: Dictionary containing product analysis
            
        Returns:
            Dictionary containing competitive analysis section
        """
        return {
            'positioning': product_analysis.get('market_positioning', {}),
            'key_differentiators': product_analysis.get(
                'competitive_analysis', {}
            ).get('advantages', []),
            'feature_comparison': product_analysis.get('common_features', {}),
            'market_presence': product_analysis.get('market_presence', {})
        }

    def generate_strengths_weaknesses(
        self,
        insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate strengths and weaknesses section.
        
        Args:
            insights: Dictionary containing competitive insights
            
        Returns:
            Dictionary containing strengths and weaknesses section
        """
        landscape = insights.get('competitive_landscape', {})
        position = landscape.get('position_analysis', {})
        
        return {
            'strengths': position.get('key_advantages', []),
            'weaknesses': position.get('key_disadvantages', []),
            'opportunities': [
                r['recommendation']
                for r in insights.get('recommendations', [])
                if r['category'] == 'Market Opportunity'
            ],
            'threats': [
                t['topic']
                for t in insights.get('trends', [])
                if any(
                    kw in t.get('keywords', [])
                    for kw in ['threat', 'risk', 'challenge']
                )
            ]
        }

    def generate_pricing_comparison(
        self,
        competitor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate pricing comparison section.
        
        Args:
            competitor_info: Dictionary containing competitor information
            
        Returns:
            Dictionary containing pricing comparison section
        """
        pricing = competitor_info.get('pricing', {})
        return {
            'pricing_model': pricing.get('model', 'N/A'),
            'price_points': pricing.get('tiers', []),
            'discounting_strategy': pricing.get('discounts', []),
            'hidden_costs': pricing.get('hidden_costs', []),
            'comparison': {
                'entry_level': pricing.get('entry_level_comparison', {}),
                'mid_tier': pricing.get('mid_tier_comparison', {}),
                'enterprise': pricing.get('enterprise_comparison', {})
            }
        }

    def generate_objection_handling(
        self,
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate objection handling section.
        
        Args:
            insights: Dictionary containing competitive insights
            
        Returns:
            List of objection handling strategies
        """
        objections = []
        
        # Add objections based on competitor strengths
        strengths = insights.get('competitive_landscape', {}).get(
            'position_analysis', {}
        ).get('key_advantages', [])
        
        for strength in strengths:
            objections.append({
                'objection': f"Competitor has {strength}",
                'response': self._generate_response(strength),
                'evidence': self._find_supporting_evidence(
                    strength,
                    insights.get('trends', [])
                )
            })
        
        # Add common objections
        common_objections = [
            'pricing',
            'features',
            'support',
            'integration',
            'security'
        ]
        
        for topic in common_objections:
            evidence = self._find_supporting_evidence(
                topic,
                insights.get('trends', [])
            )
            if evidence:
                objections.append({
                    'objection': f"Concerns about {topic}",
                    'response': self._generate_response(topic),
                    'evidence': evidence
                })
        
        return objections

    def _generate_response(self, topic: str) -> str:
        """
        Generate a response to an objection.
        
        Args:
            topic: Objection topic
            
        Returns:
            Generated response
        """
        # In production, this should use an LLM to generate responses
        return (
            f"Acknowledge the importance of {topic} and highlight our "
            "unique approach and advantages in this area."
        )

    def _find_supporting_evidence(
        self,
        topic: str,
        trends: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Find supporting evidence for a response.
        
        Args:
            topic: Topic to find evidence for
            trends: List of market trends
            
        Returns:
            List of supporting evidence
        """
        evidence = []
        topic_lower = topic.lower()
        
        for trend in trends:
            if any(
                topic_lower in keyword.lower()
                for keyword in trend.get('keywords', [])
            ):
                evidence.append(trend.get('example_text', ''))
        
        return evidence[:3]  # Return top 3 pieces of evidence

    def generate_winning_strategies(
        self,
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate winning strategies section.
        
        Args:
            insights: Dictionary containing competitive insights
            
        Returns:
            List of winning strategies
        """
        strategies = []
        
        # Add strategies based on recommendations
        for rec in insights.get('recommendations', []):
            if rec['priority'] in ['High', 'Medium']:
                strategies.append({
                    'focus_area': rec['category'],
                    'strategy': rec['recommendation'],
                    'rationale': rec['details'],
                    'expected_impact': rec['impact'],
                    'priority': rec['priority']
                })
        
        # Add strategies based on market trends
        for trend in insights.get('trends', []):
            if trend.get('document_count', 0) >= 2:
                strategies.append({
                    'focus_area': 'Market Trend',
                    'strategy': f"Leverage {trend['topic']} trend",
                    'rationale': [trend['example_text']],
                    'expected_impact': 'Market positioning',
                    'priority': 'Medium'
                })
        
        return sorted(
            strategies,
            key=lambda x: {'High': 0, 'Medium': 1, 'Low': 2}[x['priority']]
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
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
                    'template_version': self.template,
                    'competitor': input_data['competitor_info'].get('name')
                }
            }
            
            # Generate each section based on configuration
            if 'overview' in self.sections:
                battlecard['overview'] = self.generate_overview(
                    input_data['competitor_info']
                )
            
            if 'competitive_analysis' in self.sections:
                battlecard['competitive_analysis'] = (
                    self.generate_competitive_analysis(
                        input_data['product_analysis']
                    )
                )
            
            if 'strengths_weaknesses' in self.sections:
                battlecard['strengths_weaknesses'] = (
                    self.generate_strengths_weaknesses(
                        input_data['insights']
                    )
                )
            
            if 'pricing_comparison' in self.sections:
                battlecard['pricing_comparison'] = (
                    self.generate_pricing_comparison(
                        input_data['competitor_info']
                    )
                )
            
            if 'objection_handling' in self.sections:
                battlecard['objection_handling'] = (
                    self.generate_objection_handling(
                        input_data['insights']
                    )
                )
            
            if 'winning_strategies' in self.sections:
                battlecard['winning_strategies'] = (
                    self.generate_winning_strategies(
                        input_data['insights']
                    )
                )
            
            return {
                'status': 'success',
                'data': battlecard,
                'metadata': {
                    'sections_generated': list(battlecard.keys()),
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


if __name__ == "__main__":
    # Test the battlecard generation agent
    agent = BattlecardGenerationAgent({
        'template': 'standard',
        'sections': [
            'overview',
            'competitive_analysis',
            'strengths_weaknesses'
        ]
    })
    
    test_data = {
        'competitor_info': {
            'name': 'Competitor A',
            'description': 'Leading provider of cloud solutions',
            'market_share': '15%',
            'target_market': ['Enterprise', 'Mid-market'],
            'key_customers': ['Company X', 'Company Y']
        },
        'product_analysis': {
            'market_positioning': {'segment': 'Enterprise'},
            'competitive_analysis': {
                'advantages': ['Superior performance', 'Better security']
            },
            'common_features': {
                'Security': ['encryption', 'authentication'],
                'Performance': ['high', 'medium']
            }
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
    
    results = agent.process(test_data)
    print("Generated Battlecard:", json.dumps(results['data'], indent=2)) 