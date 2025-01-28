from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .base_agent import BaseAgent


class QualityCheckerAgent(BaseAgent):
    """Agent for checking data quality and flagging issues."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the quality checker agent."""
        super().__init__(config)
        self.config = config or {}
        self.min_content_length = self.config.get('min_content_length', 50)
        self.max_content_length = self.config.get('max_content_length', 10000)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.8)
        self.max_age_days = self.config.get('max_age_days', 365)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data contains required fields."""
        return isinstance(input_data.get('data'), list) and len(input_data.get('data', [])) > 0

    def check_content_length(self, content: str) -> Dict[str, Any]:
        """Check if content length is within acceptable range."""
        length = len(content)
        return {
            'valid': self.min_content_length <= length <= self.max_content_length,
            'length': length,
            'issue': (
                'Content too short' if length < self.min_content_length
                else 'Content too long' if length > self.max_content_length
                else None
            )
        }

    def check_data_freshness(self, timestamp: str) -> Dict[str, Any]:
        """Check if data is within acceptable age range."""
        try:
            data_date = datetime.fromisoformat(timestamp)
            age_days = (datetime.now() - data_date).days
            return {
                'valid': age_days <= self.max_age_days,
                'age_days': age_days,
                'issue': f'Data outdated by {age_days - self.max_age_days} days' if age_days > self.max_age_days else None
            }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'age_days': None,
                'issue': 'Invalid timestamp format'
            }

    def check_data_consistency(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for data consistency across items."""
        issues = []
        required_fields = ['content', 'timestamp', 'source']
        
        for idx, item in enumerate(items):
            item_issues = []
            
            # Check required fields
            for field in required_fields:
                if field not in item:
                    item_issues.append(f'Missing required field: {field}')
            
            # Check field types
            if 'content' in item and not isinstance(item['content'], str):
                item_issues.append('Content must be string type')
            
            if item_issues:
                issues.append({
                    'index': idx,
                    'item': item,
                    'issues': item_issues
                })
        
        return issues

    def check_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for duplicate or near-duplicate content."""
        if not items:
            return []

        contents = [item.get('content', '') for item in items]
        vectorizer = TfidfVectorizer(stop_words='english')
        
        try:
            tfidf_matrix = vectorizer.fit_transform(contents)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            duplicates = []
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    if similarity_matrix[i][j] > self.similarity_threshold:
                        duplicates.append({
                            'index1': i,
                            'index2': j,
                            'similarity': float(similarity_matrix[i][j]),
                            'items': [items[i], items[j]]
                        })
            
            return duplicates
        except Exception as e:
            self.logger.error(f"Error checking duplicates: {str(e)}")
            return []

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and check data quality."""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            items = input_data['data']
            quality_report = {
                'total_items': len(items),
                'content_issues': [],
                'freshness_issues': [],
                'consistency_issues': [],
                'duplicate_items': [],
                'overall_quality_score': 1.0
            }

            # Check content length
            for idx, item in enumerate(items):
                if 'content' in item:
                    length_check = self.check_content_length(item['content'])
                    if not length_check['valid']:
                        quality_report['content_issues'].append({
                            'index': idx,
                            'item': item,
                            'issue': length_check['issue']
                        })

            # Check data freshness
            for idx, item in enumerate(items):
                if 'timestamp' in item:
                    freshness_check = self.check_data_freshness(item['timestamp'])
                    if not freshness_check['valid']:
                        quality_report['freshness_issues'].append({
                            'index': idx,
                            'item': item,
                            'issue': freshness_check['issue']
                        })

            # Check consistency
            quality_report['consistency_issues'] = self.check_data_consistency(items)

            # Check duplicates
            quality_report['duplicate_items'] = self.check_duplicates(items)

            # Calculate overall quality score
            total_issues = (
                len(quality_report['content_issues']) +
                len(quality_report['freshness_issues']) +
                len(quality_report['consistency_issues']) +
                len(quality_report['duplicate_items'])
            )
            
            if items:
                quality_report['overall_quality_score'] = max(
                    0.0,
                    1.0 - (total_issues / len(items))
                )

            return {
                'status': 'success',
                'data': quality_report,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'config': {
                        'min_content_length': self.min_content_length,
                        'max_content_length': self.max_content_length,
                        'similarity_threshold': self.similarity_threshold,
                        'max_age_days': self.max_age_days
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error in quality checking: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }


if __name__ == "__main__":
    # Test the quality checker agent
    agent = QualityCheckerAgent({
        'min_content_length': 50,
        'max_content_length': 5000,
        'similarity_threshold': 0.8,
        'max_age_days': 180
    })
    
    test_data = {
        'data': [
            {
                'content': 'Short text',
                'timestamp': '2023-01-01T00:00:00',
                'source': 'test'
            },
            {
                'content': 'This is a longer piece of content that should pass the length check.',
                'timestamp': datetime.now().isoformat(),
                'source': 'test'
            },
            {
                'content': 'This is a similar piece of content that should pass the length check.',
                'timestamp': datetime.now().isoformat(),
                'source': 'test'
            }
        ]
    }
    
    import asyncio
    results = asyncio.run(agent.process(test_data))
    print("Quality Check Results:", results['data']) 