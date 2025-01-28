from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .base_agent import BaseAgent


class ProductAnalysisAgent(BaseAgent):
    """Agent for analyzing competitor products and features."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the product analysis agent.
        
        Args:
            config: Configuration dictionary containing analysis parameters
        """
        super().__init__(config)
        self.config = config or {}
        self.similarity_threshold = self.config.get('similarity_threshold', 0.3)
        self.min_feature_freq = self.config.get('min_feature_freq', 2)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing product data
            
        Returns:
            Boolean indicating if input is valid
        """
        required_fields = ['products', 'features']
        return all(field in input_data for field in required_fields)

    def extract_common_features(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Extract common features across products.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Dictionary of feature categories and their values
        """
        feature_categories = {}
        
        for product in products:
            for feature in product.get('features', []):
                category = feature.get('category', 'uncategorized')
                if category not in feature_categories:
                    feature_categories[category] = []
                
                value = feature.get('value', '').lower()
                if value and value not in feature_categories[category]:
                    feature_categories[category].append(value)
        
        # Filter out rare features
        for category in feature_categories:
            feature_categories[category] = [
                f for f in feature_categories[category]
                if feature_categories[category].count(f) >= self.min_feature_freq
            ]
        
        return feature_categories

    def calculate_feature_similarity(
        self,
        product1: Dict[str, Any],
        product2: Dict[str, Any]
    ) -> float:
        """
        Calculate feature similarity between two products.
        
        Args:
            product1: First product dictionary
            product2: Second product dictionary
            
        Returns:
            Similarity score between 0 and 1
        """
        # Extract feature descriptions
        features1 = ' '.join(
            f.get('value', '') for f in product1.get('features', [])
        )
        features2 = ' '.join(
            f.get('value', '') for f in product2.get('features', [])
        )
        
        # Calculate TF-IDF similarity
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([features1, features2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def find_competitive_advantages(
        self,
        target_product: Dict[str, Any],
        competitor_products: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Identify competitive advantages and disadvantages.
        
        Args:
            target_product: Product to analyze
            competitor_products: List of competitor products
            
        Returns:
            Dictionary of advantages and disadvantages
        """
        advantages = []
        disadvantages = []
        
        target_features = {
            f.get('category'): f.get('value')
            for f in target_product.get('features', [])
        }
        
        for competitor in competitor_products:
            comp_features = {
                f.get('category'): f.get('value')
                for f in competitor.get('features', [])
            }
            
            # Compare features
            for category, value in target_features.items():
                if category in comp_features:
                    comp_value = comp_features[category]
                    if self._is_better_feature(value, comp_value):
                        advantages.append(
                            f"Better {category}: {value} vs {comp_value}"
                        )
                    elif self._is_better_feature(comp_value, value):
                        disadvantages.append(
                            f"Weaker {category}: {value} vs {comp_value}"
                        )
                else:
                    advantages.append(f"Unique feature: {category} - {value}")
        
        return {
            'advantages': list(set(advantages)),
            'disadvantages': list(set(disadvantages))
        }

    def _is_better_feature(self, feature1: str, feature2: str) -> bool:
        """
        Compare two feature values to determine if first is better.
        
        Args:
            feature1: First feature value
            feature2: Second feature value
            
        Returns:
            Boolean indicating if first feature is better
        """
        # This is a simplified comparison
        # In production, implement more sophisticated comparison logic
        try:
            # Try numeric comparison
            val1 = float(feature1.split()[0])
            val2 = float(feature2.split()[0])
            return val1 > val2
        except (ValueError, IndexError):
            # For non-numeric values, use string comparison
            return feature1.lower() > feature2.lower()

    def analyze_market_positioning(
        self,
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze market positioning of products.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of product positions with similarity scores
        """
        positions = []
        n_products = len(products)
        
        # Calculate similarity matrix
        similarity_matrix = np.zeros((n_products, n_products))
        for i in range(n_products):
            for j in range(i + 1, n_products):
                similarity = self.calculate_feature_similarity(
                    products[i], products[j]
                )
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
        
        # Analyze positioning for each product
        for i, product in enumerate(products):
            similar_products = []
            for j in range(n_products):
                if i != j and similarity_matrix[i][j] > self.similarity_threshold:
                    similar_products.append({
                        'name': products[j].get('name', ''),
                        'similarity': float(similarity_matrix[i][j])
                    })
            
            positions.append({
                'product': product.get('name', ''),
                'similar_products': sorted(
                    similar_products,
                    key=lambda x: x['similarity'],
                    reverse=True
                ),
                'uniqueness_score': 1 - np.mean(similarity_matrix[i])
            })
        
        return positions

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and analyze product data.
        
        Args:
            input_data: Dictionary containing product data
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            products = input_data['products']
            target_product = products[0]  # Assume first product is target
            competitor_products = products[1:]
            
            # Perform analysis
            common_features = self.extract_common_features(products)
            competitive_analysis = self.find_competitive_advantages(
                target_product,
                competitor_products
            )
            market_positioning = self.analyze_market_positioning(products)
            
            return {
                'status': 'success',
                'data': {
                    'common_features': common_features,
                    'competitive_analysis': competitive_analysis,
                    'market_positioning': market_positioning
                },
                'metadata': {
                    'analyzed_products': len(products),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error in product analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }


if __name__ == "__main__":
    # Test the product analysis agent
    agent = ProductAnalysisAgent({
        'similarity_threshold': 0.3,
        'min_feature_freq': 2
    })
    
    test_data = {
        'products': [
            {
                'name': 'Our Product',
                'features': [
                    {'category': 'Performance', 'value': '100 ops/sec'},
                    {'category': 'Storage', 'value': '1 TB'},
                    {'category': 'Price', 'value': '$99/month'}
                ]
            },
            {
                'name': 'Competitor A',
                'features': [
                    {'category': 'Performance', 'value': '80 ops/sec'},
                    {'category': 'Storage', 'value': '500 GB'},
                    {'category': 'Price', 'value': '$79/month'}
                ]
            }
        ],
        'features': ['Performance', 'Storage', 'Price']
    }
    
    results = agent.process(test_data)
    print("Analysis Results:", results['data']) 