import os
import json
import asyncio
import aiohttp
from typing import Any, Dict, List
from datetime import datetime
from ..base import BaseAgent


class AggregatorOrchestrationAgent(BaseAgent):
    """
    Agent for aggregating competitor data from multiple sources and orchestrating
    AI-driven analysis and verification.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the aggregator agent with configuration."""
        super().__init__(config)
        self.config = config or {}
        self.brave_api_key = os.getenv("BRAVE_API_KEY", "")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.session = None

    async def setup_session(self):
        """Set up aiohttp session for async requests."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process competitor data from multiple sources and generate insights.
        
        Args:
            input_data: Dictionary containing query and context information
            
        Returns:
            Dictionary containing aggregated and analyzed results
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            await self.setup_session()

            # Extract query and context
            query = input_data.get("query", "")
            competitor_name = input_data.get("competitor_name", "")
            context = input_data.get("context", {})

            # Fetch data from multiple sources
            raw_sources = await self._fetch_all_sources(
                query=query or competitor_name,
                context=context
            )

            # Merge and deduplicate results
            merged_data = self._merge_results(raw_sources)

            # Generate initial summary
            summarized_content = await self._summarize_data(
                merged_data,
                context
            )

            # Verify accuracy
            verified_content = await self._verify_accuracy(
                summarized_content,
                merged_data
            )

            # Extract key insights
            insights = await self._extract_insights(
                verified_content,
                merged_data
            )

            return {
                "status": "success",
                "data": {
                    "query": query or competitor_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "sources": len(raw_sources),
                    "summary": verified_content,
                    "insights": insights,
                    "metadata": {
                        "confidence_score": self._calculate_confidence(merged_data),
                        "source_breakdown": self._get_source_breakdown(raw_sources),
                        "last_updated": datetime.utcnow().isoformat()
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error in aggregator processing: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            await self.cleanup()

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that input contains required fields."""
        return bool(input_data.get("query") or input_data.get("competitor_name"))

    async def _fetch_all_sources(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch data from multiple sources in parallel."""
        tasks = [
            self._fetch_from_brave_search(query),
            self._fetch_from_perplexity(query),
            self._fetch_from_internal_db(query, context),
            self._fetch_from_news_api(query),
            self._fetch_from_social_media(query)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and flatten results
        merged = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Source fetch error: {str(result)}")
                continue
            if result:
                merged.extend(result)
        
        return merged

    async def _fetch_from_brave_search(self, query: str) -> List[Dict[str, Any]]:
        """Fetch results from Brave Search API."""
        if not self.brave_api_key:
            return []

        try:
            url = "https://api.search.brave.com/search"
            headers = {"Authorization": f"Bearer {self.brave_api_key}"}
            params = {
                "q": query,
                "count": 10,
                "format": "json"
            }

            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [{
                        "source": "brave_search",
                        "type": "web_result",
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "url": item.get("url"),
                        "timestamp": datetime.utcnow().isoformat()
                    } for item in data.get("web", [])]
        except Exception as e:
            self.logger.error(f"Brave Search API error: {str(e)}")
        return []

    async def _fetch_from_perplexity(self, query: str) -> List[Dict[str, Any]]:
        """Fetch results from Perplexity-like API."""
        if not self.perplexity_api_key:
            return []

        try:
            # Replace with actual Perplexity API endpoint
            url = "https://api.perplexity.ai/search"
            headers = {"Authorization": f"Bearer {self.perplexity_api_key}"}
            data = {"query": query, "max_results": 5}

            async with self.session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    return [{
                        "source": "perplexity",
                        "type": "ai_analysis",
                        "content": item.get("content"),
                        "confidence": item.get("confidence", 0.0),
                        "timestamp": datetime.utcnow().isoformat()
                    } for item in results.get("results", [])]
        except Exception as e:
            self.logger.error(f"Perplexity API error: {str(e)}")
        return []

    async def _fetch_from_internal_db(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch relevant data from internal database."""
        try:
            # Replace with actual database query
            await asyncio.sleep(0.2)  # Simulate DB query
            return [{
                "source": "internal_db",
                "type": "historical_data",
                "content": f"Historical data about {query}",
                "timestamp": datetime.utcnow().isoformat()
            }]
        except Exception as e:
            self.logger.error(f"Internal DB error: {str(e)}")
        return []

    async def _fetch_from_news_api(self, query: str) -> List[Dict[str, Any]]:
        """Fetch recent news articles about the competitor."""
        try:
            # Replace with actual news API call
            await asyncio.sleep(0.3)  # Simulate API call
            return [{
                "source": "news_api",
                "type": "news",
                "title": f"Recent news about {query}",
                "timestamp": datetime.utcnow().isoformat()
            }]
        except Exception as e:
            self.logger.error(f"News API error: {str(e)}")
        return []

    async def _fetch_from_social_media(self, query: str) -> List[Dict[str, Any]]:
        """Fetch relevant social media mentions."""
        try:
            # Replace with actual social media API calls
            await asyncio.sleep(0.3)  # Simulate API call
            return [{
                "source": "social_media",
                "type": "social",
                "content": f"Social media mentions of {query}",
                "timestamp": datetime.utcnow().isoformat()
            }]
        except Exception as e:
            self.logger.error(f"Social media API error: {str(e)}")
        return []

    def _merge_results(self, raw_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate results from different sources."""
        # Group by source type
        grouped = {}
        for item in raw_sources:
            source_type = item.get("type", "unknown")
            if source_type not in grouped:
                grouped[source_type] = []
            grouped[source_type].append(item)

        # Deduplicate within each group
        deduplicated = []
        for items in grouped.values():
            seen_urls = set()
            for item in items:
                url = item.get("url")
                if not url or url not in seen_urls:
                    if url:
                        seen_urls.add(url)
                    deduplicated.append(item)

        return deduplicated

    async def _summarize_data(
        self,
        merged_data: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive summary using AI."""
        system_prompt = """
        You are an expert competitive intelligence analyst. Your task is to analyze
        and summarize information from multiple sources about a competitor.
        Focus on:
        1. Key business changes and market movements
        2. Product updates and feature launches
        3. Strategic implications for our business
        4. Potential opportunities and threats
        """

        # Convert data to a format suitable for the AI
        content = json.dumps(merged_data, indent=2)
        
        summary_prompt = f"""
        Analyze the following competitor information and provide a comprehensive summary:

        Context:
        {json.dumps(context, indent=2)}

        Source Data:
        {content}

        Please provide:
        1. Key findings and insights
        2. Market implications
        3. Recommended actions
        """

        return await self._call_claude(
            prompt=summary_prompt,
            system=system_prompt,
            max_tokens=2000
        )

    async def _verify_accuracy(
        self,
        summary: str,
        source_data: List[Dict[str, Any]]
    ) -> str:
        """Verify and fact-check the generated summary."""
        verification_prompt = f"""
        You are tasked with verifying the accuracy of this competitive intelligence summary:

        {summary}

        Source Data:
        {json.dumps(source_data, indent=2)}

        Please:
        1. Verify each claim against the source data
        2. Flag any unsupported or questionable statements
        3. Suggest corrections or clarifications where needed
        4. Provide confidence levels for key claims
        """

        verified_content = await self._call_claude(
            prompt=verification_prompt,
            max_tokens=1500
        )

        return verified_content

    async def _extract_insights(
        self,
        verified_content: str,
        source_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract key insights and action items."""
        insights_prompt = f"""
        Based on this verified competitive intelligence:

        {verified_content}

        Please extract:
        1. Key strategic insights
        2. Potential threats and opportunities
        3. Recommended actions
        4. Areas needing further investigation

        Format the output as a structured list of insights, each with:
        - Category (strategic, threat, opportunity, action_item)
        - Description
        - Priority (high, medium, low)
        - Confidence score (0-1)
        """

        raw_insights = await self._call_claude(
            prompt=insights_prompt,
            max_tokens=1000
        )

        # Parse and structure the insights
        try:
            insights = json.loads(raw_insights)
        except json.JSONDecodeError:
            insights = self._parse_unstructured_insights(raw_insights)

        return insights

    def _parse_unstructured_insights(self, raw_text: str) -> List[Dict[str, Any]]:
        """Parse unstructured insight text into structured format."""
        # Simple parsing logic - replace with more robust parsing if needed
        insights = []
        current_insight = {}
        
        for line in raw_text.split('\n'):
            line = line.strip()
            if not line:
                if current_insight:
                    insights.append(current_insight)
                    current_insight = {}
                continue
            
            if line.startswith('- Category:'):
                current_insight['category'] = line.split(':')[1].strip()
            elif line.startswith('- Description:'):
                current_insight['description'] = line.split(':')[1].strip()
            elif line.startswith('- Priority:'):
                current_insight['priority'] = line.split(':')[1].strip()
            elif line.startswith('- Confidence:'):
                current_insight['confidence'] = float(line.split(':')[1].strip())

        if current_insight:
            insights.append(current_insight)

        return insights

    def _calculate_confidence(self, data: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for the aggregated data."""
        if not data:
            return 0.0

        # Factors affecting confidence:
        # - Number of sources
        # - Source reliability
        # - Data freshness
        # - Consistency across sources
        
        source_weights = {
            "internal_db": 1.0,
            "perplexity": 0.8,
            "brave_search": 0.7,
            "news_api": 0.6,
            "social_media": 0.4
        }

        total_weight = 0
        weighted_sum = 0

        for item in data:
            source = item.get("source", "unknown")
            weight = source_weights.get(source, 0.3)
            
            # Adjust weight based on timestamp if available
            if timestamp := item.get("timestamp"):
                try:
                    age = (datetime.utcnow() - datetime.fromisoformat(timestamp)).days
                    if age <= 7:  # Within a week
                        weight *= 1.0
                    elif age <= 30:  # Within a month
                        weight *= 0.8
                    else:
                        weight *= 0.6
                except ValueError:
                    pass

            total_weight += weight
            weighted_sum += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _get_source_breakdown(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of data sources used."""
        breakdown = {}
        for item in data:
            source = item.get("source", "unknown")
            breakdown[source] = breakdown.get(source, 0) + 1
        return breakdown 