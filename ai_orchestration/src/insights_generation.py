from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
from .base_agent import BaseAgent


class InsightsGenerationAgent(BaseAgent):
    """Agent for generating insights from analyzed data."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the insights generation agent.
        
        Args:
            config: Configuration dictionary containing analysis parameters
        """
        super().__init__(config)
        self.config = config or {}
        self.min_cluster_size = self.config.get('min_cluster_size', 3)
        self.n_clusters = self.config.get('n_clusters', 5)
        self.min_trend_frequency = self.config.get('min_trend_frequency', 2)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing analyzed data
            
        Returns:
            Boolean indicating if input is valid
        """
        required_fields = ['summaries', 'product_analysis', 'market_data']
        return all(field in input_data for field in required_fields)

    def identify_trends(
        self,
        summaries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify trends from summarized content.
        
        Args:
            summaries: List of summary dictionaries
            
        Returns:
            List of identified trends with supporting data
        """
        # Extract text content
        texts = [s.get('summary', '') for s in summaries if s.get('summary')]
        if not texts:
            return []
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Cluster the documents
            kmeans = KMeans(
                n_clusters=min(self.n_clusters, len(texts)),
                random_state=42
            )
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Analyze each cluster
            trends = []
            for i in range(max(clusters) + 1):
                cluster_docs = [
                    text for j, text in enumerate(texts) if clusters[j] == i
                ]
                
                if len(cluster_docs) >= self.min_cluster_size:
                    # Get top terms for this cluster
                    cluster_matrix = vectorizer.transform(cluster_docs)
                    cluster_tfidf_avg = cluster_matrix.mean(axis=0).A1
                    top_term_indices = cluster_tfidf_avg.argsort()[-5:][::-1]
                    top_terms = [
                        vectorizer.get_feature_names_out()[idx]
                        for idx in top_term_indices
                    ]
                    
                    trends.append({
                        'topic': ' '.join(top_terms[:2]),
                        'keywords': top_terms,
                        'document_count': len(cluster_docs),
                        'example_text': cluster_docs[0][:200]
                    })
            
            return trends
        except Exception as e:
            self.logger.error(f"Error identifying trends: {str(e)}")
            return []

    def analyze_competitive_landscape(
        self,
        product_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze competitive landscape from product analysis.
        
        Args:
            product_analysis: Dictionary containing product analysis results
            
        Returns:
            Dictionary containing landscape analysis
        """
        try:
            common_features = product_analysis.get('common_features', {})
            competitive_analysis = product_analysis.get(
                'competitive_analysis', {}
            )
            market_positioning = product_analysis.get('market_positioning', [])
            
            # Analyze feature distribution
            feature_stats = {}
            for category, values in common_features.items():
                if values:
                    feature_stats[category] = {
                        'count': len(values),
                        'most_common': Counter(values).most_common(1)[0][0]
                    }
            
            # Analyze competitive position
            position_analysis = {
                'total_competitors': len(market_positioning) - 1,
                'average_similarity': np.mean([
                    p.get('uniqueness_score', 0)
                    for p in market_positioning
                ]),
                'key_advantages': competitive_analysis.get('advantages', []),
                'key_disadvantages': competitive_analysis.get(
                    'disadvantages', []
                )
            }
            
            return {
                'feature_analysis': feature_stats,
                'position_analysis': position_analysis
            }
        except Exception as e:
            self.logger.error(
                f"Error analyzing competitive landscape: {str(e)}"
            )
            return {}

    def generate_recommendations(
        self,
        trends: List[Dict[str, Any]],
        landscape: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations.
        
        Args:
            trends: List of identified trends
            landscape: Competitive landscape analysis
            
        Returns:
            List of recommendations with priorities
        """
        recommendations = []
        
        try:
            # Product recommendations
            advantages = landscape.get('position_analysis', {}).get(
                'key_advantages', []
            )
            disadvantages = landscape.get('position_analysis', {}).get(
                'key_disadvantages', []
            )
            
            if disadvantages:
                recommendations.append({
                    'category': 'Product Improvement',
                    'priority': 'High',
                    'recommendation': 'Address key weaknesses',
                    'details': disadvantages[:3],
                    'impact': 'Direct competitive advantage'
                })
            
            if advantages:
                recommendations.append({
                    'category': 'Marketing',
                    'priority': 'Medium',
                    'recommendation': 'Emphasize key strengths',
                    'details': advantages[:3],
                    'impact': 'Brand differentiation'
                })
            
            # Trend-based recommendations
            for trend in trends:
                if trend.get('document_count', 0) >= self.min_trend_frequency:
                    recommendations.append({
                        'category': 'Market Opportunity',
                        'priority': 'Medium',
                        'recommendation': f"Explore {trend['topic']} trend",
                        'details': [
                            f"Keywords: {', '.join(trend['keywords'])}",
                            f"Mentioned in {trend['document_count']} sources"
                        ],
                        'impact': 'Market expansion'
                    })
            
            return sorted(
                recommendations,
                key=lambda x: {'High': 0, 'Medium': 1, 'Low': 2}[x['priority']]
            )
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data and generate insights.
        
        Args:
            input_data: Dictionary containing analyzed data
            
        Returns:
            Dictionary containing generated insights
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            # Extract trends from summaries
            trends = self.identify_trends(input_data['summaries'])
            
            # Analyze competitive landscape
            landscape = self.analyze_competitive_landscape(
                input_data['product_analysis']
            )
            
            # Generate recommendations
            recommendations = self.generate_recommendations(trends, landscape)
            
            return {
                'status': 'success',
                'data': {
                    'trends': trends,
                    'competitive_landscape': landscape,
                    'recommendations': recommendations
                },
                'metadata': {
                    'trend_count': len(trends),
                    'recommendation_count': len(recommendations),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }


if __name__ == "__main__":
    # Test the insights generation agent
    agent = InsightsGenerationAgent({
        'min_cluster_size': 2,
        'n_clusters': 3,
        'min_trend_frequency': 2
    })
    
    test_data = {
        'summaries': [
            {
                'summary': """
                Cloud computing adoption continues to grow.
                Companies are investing in AI and machine learning.
                Security remains a top concern for enterprises.
                """
            },
            {
                'summary': """
                Machine learning models are becoming more accessible.
                Cloud providers offer integrated AI services.
                Cost optimization is driving cloud adoption.
                """
            }
        ],
        'product_analysis': {
            'common_features': {
                'Security': ['encryption', 'authentication'],
                'Performance': ['high', 'medium']
            },
            'competitive_analysis': {
                'advantages': ['Better security', 'Higher performance'],
                'disadvantages': ['Higher cost']
            },
            'market_positioning': [
                {'name': 'Our Product', 'uniqueness_score': 0.8},
                {'name': 'Competitor A', 'uniqueness_score': 0.6}
            ]
        },
        'market_data': {
            'market_size': 1000000,
            'growth_rate': 0.15
        }
    }
    
    results = agent.process(test_data)
    print("Generated Insights:", results['data']) 