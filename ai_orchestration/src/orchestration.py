from typing import Dict, Any, List
import asyncio
from datetime import datetime
import logging
from .base_agent import BaseAgent
from .data_collection import DataCollectionAgent
from .data_cleaning import DataCleaningAgent
from .nlp_summarization import NLPSummarizationAgent
from .product_analysis import ProductAnalysisAgent
from .insights_generation import InsightsGenerationAgent
from .battlecard_generation import (
    BattlecardGenerationAgent
)


class OrchestrationAgent(BaseAgent):
    """Agent for orchestrating the battlecard generation process."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the orchestration agent.
        
        Args:
            config: Configuration dictionary containing orchestration parameters
        """
        super().__init__(config)
        self.config = config or {}
        
        # Initialize agents
        self.agents = {
            'data_collection': DataCollectionAgent(
                self.config.get('data_collection', {})
            ),
            'data_cleaning': DataCleaningAgent(
                self.config.get('data_cleaning', {})
            ),
            'nlp_summarization': NLPSummarizationAgent(
                self.config.get('nlp_summarization', {})
            ),
            'product_analysis': ProductAnalysisAgent(
                self.config.get('product_analysis', {})
            ),
            'insights_generation': InsightsGenerationAgent(
                self.config.get('insights_generation', {})
            ),
            'battlecard_generation': BattlecardGenerationAgent(
                self.config.get('battlecard_generation', {})
            )
        }
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.log_level = self.config.get('log_level', logging.INFO)
        self.logger.setLevel(self.log_level)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing initial request data
            
        Returns:
            Boolean indicating if input is valid
        """
        required_fields = ['competitor_name', 'search_terms']
        return all(field in input_data for field in required_fields)

    async def collect_data(
        self,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect data using the data collection agent.
        
        Args:
            input_data: Dictionary containing search parameters
            
        Returns:
            Dictionary containing collected data
        """
        self.logger.info("Starting data collection")
        collection_input = {
            'search_terms': input_data['search_terms'],
            'max_pages': input_data.get('max_pages', 5)
        }
        
        try:
            result = await self.agents['data_collection'].process(
                collection_input
            )
            if result['status'] != 'success':
                raise Exception(result.get('error', 'Data collection failed'))
            return result['data']
        except Exception as e:
            self.logger.error(f"Data collection error: {str(e)}")
            raise

    async def clean_data(
        self,
        collected_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Clean collected data using the data cleaning agent.
        
        Args:
            collected_data: List of collected data items
            
        Returns:
            Dictionary containing cleaned data
        """
        self.logger.info("Starting data cleaning")
        cleaning_input = {'data': collected_data}
        
        try:
            result = await self.agents['data_cleaning'].process(cleaning_input)
            if result['status'] != 'success':
                raise Exception(result.get('error', 'Data cleaning failed'))
            return result['data']
        except Exception as e:
            self.logger.error(f"Data cleaning error: {str(e)}")
            raise

    async def summarize_data(
        self,
        cleaned_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Summarize cleaned data using the NLP summarization agent.
        
        Args:
            cleaned_data: List of cleaned data items
            
        Returns:
            Dictionary containing summarized data
        """
        self.logger.info("Starting data summarization")
        summarization_input = {'data': cleaned_data}
        
        try:
            result = await self.agents['nlp_summarization'].process(
                summarization_input
            )
            if result['status'] != 'success':
                raise Exception(result.get('error', 'Summarization failed'))
            return result['data']
        except Exception as e:
            self.logger.error(f"Summarization error: {str(e)}")
            raise

    async def analyze_products(
        self,
        input_data: Dict[str, Any],
        summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze products using the product analysis agent.
        
        Args:
            input_data: Original input data
            summaries: Summarized data
            
        Returns:
            Dictionary containing product analysis
        """
        self.logger.info("Starting product analysis")
        analysis_input = {
            'products': input_data.get('products', []),
            'features': input_data.get('features', []),
            'summaries': summaries
        }
        
        try:
            result = await self.agents['product_analysis'].process(
                analysis_input
            )
            if result['status'] != 'success':
                raise Exception(
                    result.get('error', 'Product analysis failed')
                )
            return result['data']
        except Exception as e:
            self.logger.error(f"Product analysis error: {str(e)}")
            raise

    async def generate_insights(
        self,
        summaries: List[Dict[str, Any]],
        product_analysis: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate insights using the insights generation agent.
        
        Args:
            summaries: Summarized data
            product_analysis: Product analysis results
            market_data: Market research data
            
        Returns:
            Dictionary containing generated insights
        """
        self.logger.info("Starting insights generation")
        insights_input = {
            'summaries': summaries,
            'product_analysis': product_analysis,
            'market_data': market_data
        }
        
        try:
            result = await self.agents['insights_generation'].process(
                insights_input
            )
            if result['status'] != 'success':
                raise Exception(
                    result.get('error', 'Insights generation failed')
                )
            return result['data']
        except Exception as e:
            self.logger.error(f"Insights generation error: {str(e)}")
            raise

    async def generate_battlecard(
        self,
        competitor_info: Dict[str, Any],
        product_analysis: Dict[str, Any],
        insights: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate battlecard using the battlecard generation agent.
        
        Args:
            competitor_info: Competitor information
            product_analysis: Product analysis results
            insights: Generated insights
            market_data: Market research data
            
        Returns:
            Dictionary containing generated battlecard
        """
        self.logger.info("Starting battlecard generation")
        battlecard_input = {
            'competitor_info': competitor_info,
            'product_analysis': product_analysis,
            'insights': insights,
            'market_data': market_data
        }
        
        try:
            result = await self.agents['battlecard_generation'].process(
                battlecard_input
            )
            if result['status'] != 'success':
                raise Exception(
                    result.get('error', 'Battlecard generation failed')
                )
            return result['data']
        except Exception as e:
            self.logger.error(f"Battlecard generation error: {str(e)}")
            raise

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the entire battlecard generation process.
        
        Args:
            input_data: Dictionary containing initial request data
            
        Returns:
            Dictionary containing generated battlecard and process metadata
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        start_time = datetime.now()
        process_metadata = {
            'start_time': start_time.isoformat(),
            'competitor_name': input_data['competitor_name'],
            'steps_completed': []
        }

        try:
            # Step 1: Collect data
            collected_data = await self.collect_data(input_data)
            process_metadata['steps_completed'].append('data_collection')
            
            # Step 2: Clean data
            cleaned_data = await self.clean_data(collected_data)
            process_metadata['steps_completed'].append('data_cleaning')
            
            # Step 3: Summarize data
            summarized_data = await self.summarize_data(cleaned_data)
            process_metadata['steps_completed'].append('summarization')
            
            # Step 4: Analyze products
            product_analysis = await self.analyze_products(
                input_data,
                summarized_data
            )
            process_metadata['steps_completed'].append('product_analysis')
            
            # Step 5: Generate insights
            insights = await self.generate_insights(
                summarized_data,
                product_analysis,
                input_data.get('market_data', {})
            )
            process_metadata['steps_completed'].append('insights_generation')
            
            # Step 6: Generate battlecard
            battlecard = await self.generate_battlecard(
                input_data.get('competitor_info', {}),
                product_analysis,
                insights,
                input_data.get('market_data', {})
            )
            process_metadata['steps_completed'].append('battlecard_generation')
            
            # Calculate process duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            process_metadata['end_time'] = end_time.isoformat()
            process_metadata['duration_seconds'] = duration
            
            return {
                'status': 'success',
                'data': battlecard,
                'metadata': process_metadata
            }
        except Exception as e:
            self.logger.error(f"Orchestration error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': process_metadata
            }


if __name__ == "__main__":
    # Test the orchestration agent
    async def main():
        agent = OrchestrationAgent({
            'data_collection': {
                'max_pages': 3
            },
            'nlp_summarization': {
                'model': 'facebook/bart-large-cnn'
            },
            'battlecard_generation': {
                'template': 'standard'
            }
        })
        
        test_data = {
            'competitor_name': 'Competitor A',
            'search_terms': [
                'Competitor A cloud solutions',
                'Competitor A reviews',
                'Competitor A vs'
            ],
            'competitor_info': {
                'name': 'Competitor A',
                'description': 'Leading cloud solutions provider'
            },
            'market_data': {
                'market_size': 1000000,
                'growth_rate': 0.15
            }
        }
        
        results = await agent.process(test_data)
        print(
            "Orchestration completed with status:",
            results['status']
        )
        if results['status'] == 'success':
            print(
                "Steps completed:",
                results['metadata']['steps_completed']
            )
            print(
                "Duration:",
                results['metadata']['duration_seconds'],
                "seconds"
            )
    
    asyncio.run(main()) 