import os
import asyncio
import aiohttp
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from .base_agent import BaseAgent


class DataCollectionAgent(BaseAgent):
    """Agent for collecting data from various sources."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data collection agent.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        super().__init__(config)
        self.session = None
        self.results = []

    async def setup_session(self):
        """Set up aiohttp session for async requests."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing search terms and parameters
            
        Returns:
            Boolean indicating if input is valid
        """
        required_fields = ['search_terms', 'max_pages']
        return all(field in input_data for field in required_fields)

    async def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            String containing the page content
        """
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
        return ""

    async def process_search_result(self, term: str, page: int) -> List[Dict[str, Any]]:
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
        content = await self.fetch_url(url)
        
        results = []
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                title = link.text.strip()
                if href and href.startswith('http'):
                    results.append({
                        'search_term': term,
                        'title': title,
                        'url': href,
                        'timestamp': datetime.now().isoformat()
                    })
        return results

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process search terms and collect data.
        
        Args:
            input_data: Dictionary containing search terms and parameters
            
        Returns:
            Dictionary containing collected data
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        search_terms = input_data['search_terms']
        max_pages = input_data['max_pages']

        try:
            await self.setup_session()
            tasks = []
            for term in search_terms:
                for page in range(1, max_pages + 1):
                    task = self.process_search_result(term, page)
                    tasks.append(task)

            results = await asyncio.gather(*tasks)
            # Flatten results list
            all_results = [item for sublist in results for item in sublist]
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(all_results)
            
            return {
                'status': 'success',
                'data': df.to_dict('records'),
                'metadata': {
                    'total_results': len(df),
                    'search_terms': search_terms,
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error in data collection: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'search_terms': search_terms,
                    'timestamp': datetime.now().isoformat()
                }
            }
        finally:
            await self.cleanup()


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