from typing import Dict, Any, List
import asyncio
from datetime import datetime
import logging
from .base_agent import BaseAgent
from .data_collection import DataCollectionAgent
from .data_cleaning import DataCleaningAgent
from .nlp_summarization import NLPSummarizationAgent
from .product_analysis import ProductAnalysisAgent
from .insights_generation import InsightsGenerationAgent # Generic insights
from .payer_intel_agent import PayerIntelAgent # Payer-specific insights
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
            'insights_generation': InsightsGenerationAgent( # Generic insights
                self.config.get('insights_generation', {})
            ),
            'payer_intel_agent': PayerIntelAgent( # Payer-specific insights
                self.config.get('payer_intel_agent', {}) # Add config for this if needed
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
        Can be for a generic competitor battlecard or a specific payer customer.
        """
        # For generic battlecard
        if 'competitor_name' in input_data and 'search_terms' in input_data:
            return True
        # For payer customer specific insights
        if 'customer_profile' in input_data and 'payer_identifier' in input_data and 'data_types_to_fetch' in input_data:
             # customer_profile should be a dict with at least 'name'
            if not isinstance(input_data['customer_profile'], dict) or 'name' not in input_data['customer_profile']:
                self.logger.error("Invalid 'customer_profile': must be a dict with a 'name' field.")
                return False
            return True

        self.logger.error(
            "Invalid input: Required fields for competitor_name/search_terms (for generic battlecard) "
            "OR customer_profile/payer_identifier/data_types_to_fetch (for payer insights) are missing."
        )
        return False

    async def _collect_data_for_orchestration(
        self,
        input_data: Dict[str, Any] # Contains all initial parameters for the orchestration
    ) -> Dict[str, Any]:
        """
        Collects data using the DataCollectionAgent.
        The input_data for DataCollectionAgent is constructed based on the orchestration type.
        """
        self.logger.info("Orchestration step: Data Collection")
        
        # Default to generic search if not specified for payer
        collection_agent_input = {
            'search_terms': input_data.get('search_terms', []), # For generic competitive intel
            'max_pages': input_data.get('max_pages', 1), # Default to 1 for generic
            'payer_identifier': input_data.get('payer_identifier'), # For specific payer
            'contract_id': input_data.get('contract_id'), # Optional, might be same as payer_identifier
            'data_types_to_fetch': input_data.get('data_types_to_fetch', []) # e.g. ['landscape', 'enrollment']
        }
        # Filter out None values to keep DataCollectionAgent's input clean
        collection_agent_input = {k: v for k, v in collection_agent_input.items() if v is not None}

        if not collection_agent_input.get('search_terms') and not collection_agent_input.get('payer_identifier'):
            self.logger.warning("No search terms or payer_identifier provided for data collection.")
            return {'generic_web_search': [], 'cms_data': {}} # Return empty structure

        try:
            result = await self.agents['data_collection'].process(collection_agent_input)
            if result['status'] != 'success':
                self.logger.error(f"Data collection failed: {result.get('error', 'Unknown error')}")
                # Return empty structure or raise specific error
                return {'generic_web_search': [], 'cms_data': {}}
            return result['data'] # This should now return a dict like {'generic_web_search': [...], 'cms_data': {...}}
        except Exception as e:
            self.logger.error(f"Exception in data collection: {str(e)}", exc_info=True)
            raise # Re-raise to be caught by the main process loop

    async def _clean_collected_data( # Renamed from clean_data
        self,
        # collected_data is now a dict with 'generic_web_search' and 'cms_data'
        collected_data_dict: Dict[str, Any]
    ) -> Dict[str, Any]: # Returns a similar dict structure with cleaned data
        """
        Clean collected data using the DataCleaningAgent.
        Focuses on cleaning 'generic_web_search' results.
        CMS data is assumed to be relatively clean but could have specific cleaning here.
        """
        self.logger.info("Orchestration step: Data Cleaning")
        cleaned_data_output = {'cleaned_generic_web_search': [], 'cleaned_cms_data': collected_data_dict.get('cms_data', {})}

        generic_web_data = collected_data_dict.get('generic_web_search')
        if generic_web_data:
            self.logger.info(f"Cleaning {len(generic_web_data)} generic web search results.")
            cleaning_input = {'data': generic_web_data} # DataCleaningAgent expects a list
            try:
                result = await self.agents['data_cleaning'].process(cleaning_input)
                if result['status'] == 'success':
                    cleaned_data_output['cleaned_generic_web_search'] = result['data']
                else:
                    self.logger.error(f"Data cleaning for web results failed: {result.get('error', 'Unknown error')}")
                    # Decide: return partially cleaned data or raise error? For now, log and continue.
                    cleaned_data_output['cleaned_generic_web_search'] = generic_web_data # Fallback to uncleaned
            except Exception as e:
                self.logger.error(f"Exception in data cleaning for web results: {str(e)}", exc_info=True)
                cleaned_data_output['cleaned_generic_web_search'] = generic_web_data # Fallback
        
        # Placeholder for CMS data specific cleaning if needed
        # For example, ensuring consistent column names or data types from different CMS files
        # cleaned_data_output['cleaned_cms_data'] = self._clean_cms_data(collected_data_dict.get('cms_data', {}))

        return cleaned_data_output

    async def _summarize_cleaned_data( # Renamed from summarize_data
        self,
        # Takes the output from _clean_collected_data
        cleaned_data_dict: Dict[str, Any]
    ) -> List[Dict[str, Any]]: # Returns a list of summaries (primarily from web search)
        """
        Summarize cleaned data using the NLP summarization agent.
        Primarily targets cleaned generic web search results.
        """
        self.logger.info("Orchestration step: Data Summarization")
        summaries = []
        
        cleaned_web_data = cleaned_data_dict.get('cleaned_generic_web_search')
        if cleaned_web_data:
            self.logger.info(f"Summarizing {len(cleaned_web_data)} cleaned web search results.")
            # NLPSummarizationAgent expects a list of items with text to summarize
            # Assuming DataCleaningAgent output is a list of dicts, each potentially having 'text_content' or similar
            # This might need adjustment based on actual DataCleaningAgent output structure
            summarization_input = {'data': cleaned_web_data}
            try:
                result = await self.agents['nlp_summarization'].process(summarization_input)
                if result['status'] == 'success':
                    summaries = result['data'] # Expecting a list of summary dicts
                else:
                    self.logger.error(f"Data summarization failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                self.logger.error(f"Exception in data summarization: {str(e)}", exc_info=True)
        else:
            self.logger.info("No generic web data to summarize.")

        return summaries # List of summary dicts

    async def _analyze_products_and_market( # Renamed from analyze_products
        self,
        input_data: Dict[str, Any], # Original orchestration input
        web_summaries: List[Dict[str, Any]] # Summaries from generic web search
    ) -> Dict[str, Any]: # Returns product analysis dict
        """
        Analyze products using the product analysis agent.
        This is typically for competitive analysis.
        """
        self.logger.info("Orchestration step: Product and Market Analysis (Generic)")
        # This agent might be more relevant for competitor battlecards than payer insights directly
        # unless 'products' in input_data refers to competitor products relevant to the payer.
        analysis_input = {
            'products': input_data.get('products', []), # e.g., competitor products
            'features': input_data.get('features', []), # e.g., features of those products
            'summaries': web_summaries # Use web summaries for context
        }
        
        product_analysis_data = {}
        try:
            result = await self.agents['product_analysis'].process(analysis_input)
            if result['status'] == 'success':
                product_analysis_data = result['data']
            else:
                self.logger.error(f"Product analysis failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.logger.error(f"Exception in product analysis: {str(e)}", exc_info=True)

        return product_analysis_data

    async def _generate_generic_insights( # Renamed from generate_insights
        self,
        web_summaries: List[Dict[str, Any]],
        product_analysis_data: Dict[str, Any], # Output from _analyze_products_and_market
        input_data: Dict[str, Any] # Original orchestration input for market_data
    ) -> Dict[str, Any]: # Returns generic insights dict
        """
        Generate generic insights using the InsightsGenerationAgent.
        This is typically based on web summaries and product/market analysis.
        """
        self.logger.info("Orchestration step: Generic Insights Generation")
        insights_input = {
            'summaries': web_summaries,
            'product_analysis': product_analysis_data,
            'market_data': input_data.get('market_data', {}) # Get market_data from original input
        }
        
        generic_insights_data = {}
        try:
            result = await self.agents['insights_generation'].process(insights_input)
            if result['status'] == 'success':
                generic_insights_data = result['data']
            else:
                self.logger.error(f"Generic insights generation failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.logger.error(f"Exception in generic insights generation: {str(e)}", exc_info=True)

        return generic_insights_data

    async def _generate_payer_specific_insights(
        self,
        collected_data_dict: Dict[str, Any], # Contains 'cms_data' and 'generic_web_search'
        customer_profile: Dict[str, Any] # From original input_data
    ) -> Dict[str, Any]:
        """
        Generate payer-specific insights using the PayerIntelAgent.
        """
        self.logger.info(f"Orchestration step: Payer Specific Insights Generation for {customer_profile.get('name', 'Unknown Payer')}")

        payer_intel_input = {
            'cms_data': collected_data_dict.get('cms_data', {}),
            'generic_web_search': collected_data_dict.get('generic_web_search', []), # PayerIntelAgent expects a list
            'customer_profile': customer_profile
        }

        payer_insights_data = {}
        try:
            result = await self.agents['payer_intel_agent'].process(payer_intel_input)
            if result['status'] == 'success':
                payer_insights_data = result['data'] # This will contain llm_generated_insights, etc.
            else:
                self.logger.error(f"Payer specific insights generation failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.logger.error(f"Exception in payer specific insights generation: {str(e)}", exc_info=True)

        return payer_insights_data

    async def _generate_final_battlecard_or_report( # Renamed from generate_battlecard
        self,
        input_data: Dict[str, Any], # Original orchestration input
        product_analysis_data: Dict[str, Any],
        # Combined insights: could be generic, payer-specific, or merged
        all_insights_data: Dict[str, Any]
    ) -> Dict[str, Any]: # Returns battlecard/report dict
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
            # Log the invalid input for debugging, but don't include sensitive data in production logs
            self.logger.error(f"Invalid input data received by OrchestrationAgent. Keys: {list(input_data.keys())}")
            return {
                'status': 'error',
                'error': 'Invalid input data format for orchestration.',
                'metadata': {'timestamp': datetime.now().isoformat()}
            }

        start_time = datetime.now()
        process_metadata = { # Initialize with common fields
            'start_time': start_time.isoformat(),
            'steps_completed': []
        }
        # Add context-specific identifiers to metadata
        if 'customer_profile' in input_data:
            process_metadata['customer_name'] = input_data['customer_profile'].get('name', 'Unknown Customer')
        elif 'competitor_name' in input_data:
            process_metadata['competitor_name'] = input_data['competitor_name']


        final_output_data = {}

        try:
            # Step 1: Collect data (handles both generic web and specific payer data)
            # collected_data_dict will have keys like 'generic_web_search', 'cms_data'
            collected_data_dict = await self._collect_data_for_orchestration(input_data)
            process_metadata['steps_completed'].append('data_collection')
            
            # Step 2: Clean data (primarily web data, CMS data might have its own cleaning or be used as is)
            # cleaned_data_dict will have 'cleaned_generic_web_search', 'cleaned_cms_data'
            cleaned_data_dict = await self._clean_collected_data(collected_data_dict)
            process_metadata['steps_completed'].append('data_cleaning')
            
            # Step 3: Summarize cleaned web data
            web_summaries = await self._summarize_cleaned_data(cleaned_data_dict)
            process_metadata['steps_completed'].append('summarization')
            
            # Step 4: Analyze products and market (typically for competitive context)
            # This uses web_summaries and original input_data for product/feature lists
            product_analysis_data = await self._analyze_products_and_market(input_data, web_summaries)
            process_metadata['steps_completed'].append('product_analysis')
            
            # Step 5: Generate Insights - can be generic, payer-specific, or both
            all_insights_data = {}
            if 'customer_profile' in input_data:
                # Generate payer-specific insights
                payer_insights = await self._generate_payer_specific_insights(
                    collected_data_dict, # Pass raw collected data (PayerIntelAgent handles its own analysis of CMS parts)
                    input_data['customer_profile']
                )
                all_insights_data['payer_specific'] = payer_insights
                process_metadata['steps_completed'].append('payer_insights_generation')
                final_output_data = payer_insights # For payer context, these insights are the primary output
            else:
                # Generate generic insights (e.g., for a competitor battlecard)
                generic_insights = await self._generate_generic_insights(
                    web_summaries,
                    product_analysis_data,
                    input_data
                )
                all_insights_data['generic'] = generic_insights
                process_metadata['steps_completed'].append('generic_insights_generation')

                # Step 6 (Conditional): Generate Battlecard (typically for competitor context)
                # If it's not a payer-specific insight request, generate a battlecard
                battlecard_data = await self._generate_final_battlecard_or_report(
                    input_data, # Contains competitor_info, market_data etc.
                    product_analysis_data,
                    all_insights_data
                )
                final_output_data = battlecard_data # For competitor context, battlecard is primary output
                process_metadata['steps_completed'].append('battlecard_generation')

            # Calculate process duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            process_metadata['end_time'] = end_time.isoformat()
            process_metadata['duration_seconds'] = duration
            
            return {
                'status': 'success',
                'data': final_output_data, # Contains payer insights or battlecard
                'metadata': process_metadata
            }
        except Exception as e:
            self.logger.error(f"Orchestration error: {str(e)}", exc_info=True)
            # Ensure essential metadata is present even in error cases
            process_metadata['end_time'] = datetime.now().isoformat()
            process_metadata['duration_seconds'] = (datetime.now() - start_time).total_seconds()
            return {
                'status': 'error',
                'error': str(e),
                'metadata': process_metadata
            }


if __name__ == "__main__":
    # Test the orchestration agent
    async def main():
        # Generic Competitor Battlecard Test
        agent_comp = OrchestrationAgent({
            'data_collection': {'max_pages': 1}, # Keep it small for test
            'payer_intel_agent': {} # Empty config for now
        })
        test_data_competitor = {
            'competitor_name': 'Competitor A',
            'search_terms': ['Competitor A cloud solutions', 'Competitor A reviews'],
            'competitor_info': {'name': 'Competitor A', 'description': 'Leading cloud solutions provider'},
            'market_data': {'market_size': 1000000, 'growth_rate': 0.15},
            'products': [{'name': 'Competitor X Product', 'features': ['fast', 'cheap']}]
        }
        print("\n--- Testing Generic Competitor Battlecard ---")
        results_comp = await agent_comp.process(test_data_competitor)
        print(f"Competitor Battlecard Orchestration Status: {results_comp['status']}")
        if results_comp['status'] == 'success':
            print(f"  Steps: {results_comp['metadata']['steps_completed']}")
            print(f"  Duration: {results_comp['metadata']['duration_seconds']:.2f}s")
            # print(f"  Data: {results_comp['data']}") # Can be verbose
        else:
            print(f"  Error: {results_comp.get('error')}")

        # Payer Specific Insights Test
        agent_payer = OrchestrationAgent({
            'data_collection': { # Config for DataCollectionAgent
                'cms_base_url': "https://data.cms.gov/provider-data/api/1/datastore/query/" # Example
            },
            'payer_intel_agent': { # Config for PayerIntelAgent
                # 'llm_api_key': 'YOUR_LLM_KEY_HERE', # Example
                # 'llm_endpoint': 'YOUR_LLM_ENDPOINT_HERE' # Example
            }
        })
        test_data_payer = {
            'customer_profile': {
                'id': 123, # From our DB
                'name': 'Big Health Payer Inc.',
                'business_model': 'National PPO Network',
                'membership_count': 5000000
            },
            'payer_identifier': 'BHPINC', # Hypothetical identifier for CMS or internal use
            'contract_id': 'H0001', # Example CMS contract ID
            'data_types_to_fetch': ['landscape', 'star_ratings'], # What specific CMS data to get
            # Optionally, add generic search terms for this payer too
            'search_terms': ['Big Health Payer Inc. news', 'Big Health Payer Inc. strategy'],
            'max_pages': 1
        }
        print("\n--- Testing Payer Specific Insights ---")
        results_payer = await agent_payer.process(test_data_payer)
        print(f"Payer Insights Orchestration Status: {results_payer['status']}")
        if results_payer['status'] == 'success':
            print(f"  Steps: {results_payer['metadata']['steps_completed']}")
            print(f"  Duration: {results_payer['metadata']['duration_seconds']:.2f}s")
            print(f"  LLM Insights: {results_payer['data'].get('llm_generated_insights', 'N/A')}")
            # print(f"  Full Payer Data: {results_payer['data']}") # Can be verbose
        else:
            print(f"  Error: {results_payer.get('error')}")

    asyncio.run(main()) 