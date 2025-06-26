import os
import asyncio
import aiohttp
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io # Required for StringIO

from .base_agent import BaseAgent


class DataCollectionAgent(BaseAgent):
    """Agent for collecting data from various sources, including CMS.gov."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data collection agent.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        super().__init__(config)
        self.session = None
        self.results = []
        self.cms_base_url = config.get("cms_base_url", "https://data.cms.gov/provider-data/api/1/datastore/query/") # Example, adjust as needed

    async def _get_aiohttp_session(self):
        """Ensure aiohttp session is available."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _close_aiohttp_session(self):
        """Clean up aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _fetch_csv_data(self, url: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Fetch and parse CSV data from a URL.
        Uses aiohttp for async requests.
        """
        session = await self._get_aiohttp_session() # Renamed from setup_session
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status() # Raise an exception for HTTP errors
                content = await response.text() # Make sure this is awaited
                return pd.read_csv(io.StringIO(content))
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching CSV from {url}: {e}")
            return pd.DataFrame() # Return empty DataFrame on error
        except pd.errors.ParserError as e:
            self.logger.error(f"Error parsing CSV from {url}: {e}")
            return pd.DataFrame()
        # No finally block to close session here, manage session lifecycle separately

    async def fetch_ma_landscape_data(self, payer_identifier: str) -> pd.DataFrame:
        """
        Fetch Medicare Advantage plan landscape data for a given payer.
        Placeholder: Actual CMS endpoint URL and query params are needed.
        """
        self.logger.warning(
            "Placeholder: fetch_ma_landscape_data needs actual CMS endpoint URL and query parameters "
            f"for payer_identifier: {payer_identifier}"
        )
        # Example structure (replace with actual API call):
        # landscape_url = f"{self.cms_base_url}/some_landscape_dataset_id/query"
        # params = {"filter_column": "parent_organization", "filter_value": payer_identifier, "format": "csv"}
        # return await self._fetch_csv_data(landscape_url, params=params)
        return pd.DataFrame()

    async def fetch_ma_enrollment_data(self, contract_id: str, year: int, month: int) -> pd.DataFrame:
        """
        Fetch Medicare Advantage enrollment data for a specific contract and period.
        Placeholder: Actual CMS endpoint URL and query params are needed.
        """
        self.logger.warning(
            "Placeholder: fetch_ma_enrollment_data needs actual CMS endpoint URL and query parameters "
            f"for contract_id: {contract_id}, year: {year}, month: {month}"
        )
        # Example structure:
        # enrollment_url = f"{self.cms_base_url}/some_enrollment_dataset_id/query"
        # params = {"contract_id": contract_id, "year": year, "month": month, "format": "csv"}
        # return await self._fetch_csv_data(enrollment_url, params=params)
        return pd.DataFrame()

    async def fetch_ma_star_ratings(self, contract_id: str, year: int) -> pd.DataFrame:
        """
        Fetch Medicare Advantage Star Ratings for a specific contract and year.
        Placeholder: Actual CMS endpoint URL and query params are needed.
        """
        self.logger.warning(
            "Placeholder: fetch_ma_star_ratings needs actual CMS endpoint URL and query parameters "
            f"for contract_id: {contract_id}, year: {year}"
        )
        # Example structure:
        # star_ratings_url = f"{self.cms_base_url}/some_star_ratings_dataset_id/query"
        # params = {"contract_id": contract_id, "year": year, "format": "csv"}
        # return await self._fetch_csv_data(star_ratings_url, params=params)
        return pd.DataFrame()

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        For generic web search: 'search_terms', 'max_pages'.
        For payer-specific data: 'payer_name' or 'contract_id', 'data_types_to_fetch'.
        """
        if 'search_terms' in input_data and 'max_pages' in input_data:
            return True # For generic search
        if 'payer_identifier' in input_data and 'data_types_to_fetch' in input_data:
            return True # For payer-specific CMS data

        self.logger.error("Invalid input: Missing required fields for either generic search or payer-specific data collection.")
        return False

    async def _fetch_generic_url_content(self, url: str) -> str:
        """
        Fetch raw content from a generic URL. (Renamed from fetch_url)
        """
        session = await self._get_aiohttp_session()
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
        return ""

    async def _process_generic_search_result(self, term: str, page: int) -> List[Dict[str, Any]]:
        """
        Process a single search result page.
        
        Args:
            term: Search term
            page: Page number
            
        Returns:
            List of dictionaries containing search results
        """
        # This is a placeholder. In production, use proper search APIs
        url = f"https://example.com/search?q={term}&page={page}"
        content = await self._fetch_generic_url_content(url) # Use renamed method
        
        results = []
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            # Basic link extraction, can be improved
            for link_tag in soup.find_all('a', href=True):
                href = link_tag['href']
                title = link_tag.get_text(strip=True)
                if href.startswith('http'): # Basic filter for valid URLs
                    results.append({
                        'search_term': term,
                        'title': title,
                        'url': href,
                        'source_type': 'generic_web_search',
                        'collected_at': datetime.now().isoformat()
                    })
        return results

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data to collect information.
        Can handle generic web searches or specific payer data collection from CMS.
        """
        if not self.validate_input(input_data):
            return {
                'status': 'error',
                'error': 'Invalid input data format',
                'metadata': {'timestamp': datetime.now().isoformat()}
            }

        all_collected_data = {}
        tasks = []

        # Ensure session is created at the beginning of processing
        await self._get_aiohttp_session()

        try:
            if 'search_terms' in input_data: # Generic web search
                self.logger.info(f"Starting generic web search for terms: {input_data['search_terms']}")
                search_terms = input_data['search_terms']
                max_pages = input_data.get('max_pages', 1) # Default to 1 page if not specified

                search_tasks = []
                for term in search_terms:
                    for page_num in range(1, max_pages + 1):
                        search_tasks.append(self._process_generic_search_result(term, page_num))

                generic_results_list = await asyncio.gather(*search_tasks)
                all_collected_data['generic_web_search'] = [item for sublist in generic_results_list for item in sublist]
                self.logger.info(f"Collected {len(all_collected_data['generic_web_search'])} generic web results.")

            if 'payer_identifier' in input_data: # Payer-specific data collection
                payer_id = input_data['payer_identifier']
                data_types = input_data.get('data_types_to_fetch', []) # e.g., ['landscape', 'enrollment', 'star_ratings']
                current_year = datetime.now().year
                current_month = datetime.now().month

                self.logger.info(f"Starting payer-specific data collection for {payer_id}, types: {data_types}")

                cms_data_frames = {}
                if 'landscape' in data_types:
                    landscape_df = await self.fetch_ma_landscape_data(payer_id)
                    if not landscape_df.empty:
                        cms_data_frames['ma_landscape'] = landscape_df.to_dict('records')

                # Assuming contract_id might be same as payer_id or derived from landscape
                # This part needs refinement based on how contract_id is obtained
                contract_id_for_cms = input_data.get('contract_id', payer_id)

                if 'enrollment' in data_types:
                    enrollment_df = await self.fetch_ma_enrollment_data(contract_id_for_cms, current_year, current_month)
                    if not enrollment_df.empty:
                         cms_data_frames['ma_enrollment'] = enrollment_df.to_dict('records')

                if 'star_ratings' in data_types:
                    ratings_df = await self.fetch_ma_star_ratings(contract_id_for_cms, current_year)
                    if not ratings_df.empty:
                        cms_data_frames['ma_star_ratings'] = ratings_df.to_dict('records')

                if cms_data_frames:
                    all_collected_data['cms_data'] = cms_data_frames
                self.logger.info(f"Collected CMS data for {payer_id}: {list(cms_data_frames.keys())}")
            
            if not all_collected_data:
                 return {
                    'status': 'success',
                    'data': {},
                    'message': 'No data collection tasks were specified or no data found.',
                    'metadata': {'timestamp': datetime.now().isoformat()}
                }

            return {
                'status': 'success',
                'data': all_collected_data,
                'metadata': {
                    'input_params': input_data, # Echo input for clarity
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error during data collection process: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {'timestamp': datetime.now().isoformat()}
            }
        finally:
            await self._close_aiohttp_session() # Ensure session is closed


if __name__ == "__main__":
    async def main():
        agent = DataCollectionAgent()
        input_data = {
            'search_terms': ['Company A', 'Company B'],
            'max_pages': 3
        }
        results = await agent.process(input_data)
        print(f"Collected {len(results['data'])} results")

    asyncio.run(main()) 