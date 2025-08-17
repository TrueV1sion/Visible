import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse, urljoin
import re
from ..core.exceptions import ExternalAPIError, ValidationError
from ..schemas.validation import validate_external_url, sanitize_html_content
from .base_agent import BaseAgent


class SecureDataCollectionAgent(BaseAgent):
    """Secure agent for collecting data from validated external sources."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with enhanced security configuration."""
        super().__init__(config)
        
        # Security settings
        self.allowed_domains = self.config.get('allowed_domains', [
            'example.com', 'news.com', 'industry-reports.com'
        ])
        self.max_content_size = self.config.get('max_content_size', 1024 * 1024)  # 1MB
        self.max_redirects = self.config.get('max_redirects', 3)
        self.user_agent = self.config.get('user_agent', 'BattlecardBot/1.0')
        
        # Rate limiting
        self.rate_limit = self.config.get('rate_limit', 1)  # requests per second
        self.last_request_time = 0
        
        # Session configuration
        self.session = None
        self.connector = None

    async def setup_session(self):
        """Set up secure aiohttp session with proper configuration."""
        if not self.session:
            # Configure connection limits and security
            connector = aiohttp.TCPConnector(
                limit=10,  # Total connection pool size
                limit_per_host=5,  # Connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                ssl=True  # Force SSL verification
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.timeout,
                connect=10,
                sock_read=10
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': self.user_agent
                },
                max_redirects=self.max_redirects
            )

    async def cleanup(self):
        """Clean up resources safely."""
        if self.session:
            await self.session.close()
            self.session = None

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Enhanced input validation with security checks."""
        if not super().validate_input(input_data):
            return False
        
        required_fields = ['search_terms', 'max_pages']
        if not all(field in input_data for field in required_fields):
            return False
        
        # Validate search terms
        search_terms = input_data.get('search_terms', [])
        if not isinstance(search_terms, list) or len(search_terms) == 0:
            return False
        
        # Check for malicious content in search terms
        for term in search_terms:
            if not isinstance(term, str) or len(term) > 200:
                return False
            # Basic XSS prevention
            if re.search(r'[<>"\']', term):
                return False
        
        # Validate max_pages
        max_pages = input_data.get('max_pages', 0)
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 20:
            return False
        
        return True

    async def fetch_url_secure(self, url: str) -> Optional[str]:
        """Securely fetch content from a URL with validation."""
        try:
            # Validate URL domain
            if not validate_external_url(url, self.allowed_domains):
                self.logger.warning(
                    "URL rejected - domain not in allowlist",
                    url=url,
                    allowed_domains=self.allowed_domains
                )
                return None
            
            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < (1.0 / self.rate_limit):
                await asyncio.sleep((1.0 / self.rate_limit) - time_since_last)
            
            self.last_request_time = current_time
            
            # Make secure request
            async with self.session.get(url) as response:
                # Check response status
                if response.status != 200:
                    self.logger.warning(
                        "HTTP error response",
                        url=url,
                        status=response.status
                    )
                    return None
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith(('text/html', 'text/plain', 'application/json')):
                    self.logger.warning(
                        "Invalid content type",
                        url=url,
                        content_type=content_type
                    )
                    return None
                
                # Check content size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_content_size:
                    self.logger.warning(
                        "Content too large",
                        url=url,
                        content_length=content_length,
                        max_size=self.max_content_size
                    )
                    return None
                
                # Read content with size limit
                content = ""
                bytes_read = 0
                async for chunk in response.content.iter_chunked(8192):
                    bytes_read += len(chunk)
                    if bytes_read > self.max_content_size:
                        self.logger.warning(
                            "Content size exceeded during reading",
                            url=url,
                            bytes_read=bytes_read
                        )
                        return None
                    content += chunk.decode('utf-8', errors='ignore')
                
                # Sanitize content
                return sanitize_html_content(content)
                
        except Exception as e:
            self.logger.error(
                "Error fetching URL",
                url=url,
                error=str(e),
                error_type=type(e).__name__
            )
            return None

    async def extract_structured_data(self, url: str, content: str) -> Dict[str, Any]:
        """Extract structured data from HTML content."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # Extract main content (remove script, style, nav, footer)
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            text_content = main_content.get_text() if main_content else soup.get_text()
            
            # Clean and normalize text
            text_content = ' '.join(text_content.split())[:5000]  # Limit to 5000 chars
            
            return {
                'url': url,
                'title': title_text[:200],  # Limit title length
                'description': description[:500],  # Limit description
                'content': text_content,
                'extracted_at': datetime.now().isoformat(),
                'content_length': len(text_content)
            }
            
        except Exception as e:
            self.logger.error(
                "Error extracting structured data",
                url=url,
                error=str(e)
            )
            return {
                'url': url,
                'title': '',
                'description': '',
                'content': content[:1000],  # Fallback to raw content
                'extracted_at': datetime.now().isoformat(),
                'error': str(e)
            }

    async def search_mock_data(self, term: str, page: int) -> List[Dict[str, Any]]:
        """Generate mock search results for testing."""
        # In production, this would integrate with real search APIs
        base_results = [
            {
                'title': f'Company Information for {term}',
                'url': f'https://example.com/company/{term.lower().replace(" ", "-")}',
                'description': f'Comprehensive information about {term} and their products.'
            },
            {
                'title': f'{term} Recent News',
                'url': f'https://news.com/companies/{term.lower().replace(" ", "-")}',
                'description': f'Latest news and updates about {term}.'
            },
            {
                'title': f'{term} Product Reviews',
                'url': f'https://example.com/reviews/{term.lower().replace(" ", "-")}',
                'description': f'Customer reviews and ratings for {term} products.'
            }
        ]
        
        # Simulate pagination
        start_idx = (page - 1) * 3
        end_idx = start_idx + 3
        page_results = base_results[start_idx:end_idx]
        
        return [
            {
                **result,
                'search_term': term,
                'page': page,
                'timestamp': datetime.now().isoformat()
            }
            for result in page_results
        ]

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process search terms and collect data securely."""
        search_terms = input_data['search_terms']
        max_pages = input_data['max_pages']

        try:
            await self.setup_session()
            all_results = []
            
            # Process each search term
            for term in search_terms:
                term_results = []
                
                for page in range(1, max_pages + 1):
                    try:
                        # Get search results (mock implementation)
                        search_results = await self.search_mock_data(term, page)
                        
                        # Fetch and process each URL
                        for result in search_results:
                            url = result['url']
                            content = await self.fetch_url_secure(url)
                            
                            if content:
                                structured_data = await self.extract_structured_data(url, content)
                                structured_data.update({
                                    'search_term': term,
                                    'search_result_title': result['title'],
                                    'search_result_description': result['description']
                                })
                                term_results.append(structured_data)
                        
                        # Add delay between pages
                        await asyncio.sleep(1.0 / self.rate_limit)
                        
                    except Exception as e:
                        self.logger.error(
                            "Error processing search page",
                            term=term,
                            page=page,
                            error=str(e)
                        )
                
                all_results.extend(term_results)
            
            # Convert to DataFrame for easier processing
            if all_results:
                df = pd.DataFrame(all_results)
            else:
                df = pd.DataFrame()
            
            return {
                'status': 'success',
                'data': df.to_dict('records') if not df.empty else [],
                'metadata': {
                    'total_results': len(all_results),
                    'search_terms': search_terms,
                    'pages_processed': max_pages,
                    'timestamp': datetime.now().isoformat(),
                    'agent_health': self.get_health_status()
                }
            }
            
        except Exception as e:
            self.logger.error(
                "Data collection failed",
                search_terms=search_terms,
                error=str(e)
            )
            return {
                'status': 'error',
                'error': str(e),
                'error_code': 'DATA_COLLECTION_FAILED',
                'metadata': {
                    'search_terms': search_terms,
                    'timestamp': datetime.now().isoformat()
                }
            }
        finally:
            await self.cleanup()