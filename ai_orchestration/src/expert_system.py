from typing import Dict, Any, List
from datetime import datetime
import numpy as np
import yaml
import logging.config
from pathlib import Path
from .base_agent import BaseAgent


class ExpertSystemAgent(BaseAgent):
    """Agent for making expert decisions about products and recommendations."""

    def __init__(self, config_path: str = None):
        """Initialize the expert system agent with configuration."""
        config = self._load_config(config_path)
        super().__init__(config)
        
        # Set up logging
        self._setup_logging(config.get('logging', {}))
        
        # Load configuration sections
        self.weights = config.get('weights', {})
        self.market_segments = config.get('market_segments', {})
        self.thresholds = config.get('thresholds', {})
        self.feature_weights = config.get('feature_weights', {})
        self.market_presence = config.get('market_presence', {})
        self.sentiment = config.get('sentiment_analysis', {})
        self.priorities = config.get('priorities', {})
        
        # Initialize cache if enabled
        self.cache_config = config.get('cache', {})
        self.cache = {} if self.cache_config.get('enabled') else None
        self.cache_ttl = self.cache_config.get('ttl', 3600)
        self.cache_max_size = self.cache_config.get('max_size', 1000)

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_dir = Path(__file__).parent.parent.parent / 'config'
        default_path = config_dir / 'expert_system.yaml'
        config_path = config_path or default_path
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {}

    def _setup_logging(self, log_config: Dict[str, Any]):
        """Configure logging based on settings."""
        if log_config:
            try:
                # Ensure log directory exists
                log_file = log_config.get('file')
                if log_file:
                    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Configure logging
                logging.config.dictConfig({
                    'version': 1,
                    'formatters': {
                        'default': {
                            'format': log_config.get('format')
                        }
                    },
                    'handlers': {
                        'file': {
                            'class': 'logging.handlers.RotatingFileHandler',
                            'filename': log_file,
                            'maxBytes': log_config.get('max_size', 10485760),
                            'backupCount': log_config.get('backup_count', 5),
                            'formatter': 'default'
                        }
                    },
                    'root': {
                        'level': log_config.get('level', 'INFO'),
                        'handlers': ['file']
                    }
                })
            except Exception as e:
                self.logger.error(f"Error setting up logging: {str(e)}")

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data contains required fields."""
        required_fields = ['products', 'market_data', 'customer_data']
        return all(field in input_data for field in required_fields)

    def calculate_feature_score(
        self,
        product: Dict[str, Any],
        competitor: Dict[str, Any]
    ) -> float:
        """Calculate feature comparison score with weighted features."""
        our_features = set(product.get('features', []))
        their_features = set(competitor.get('features', []))
        
        # Calculate weighted feature scores
        our_score = sum(
            self.feature_weights.get(feature, 1.0)
            for feature in our_features
        )
        their_score = sum(
            self.feature_weights.get(feature, 1.0)
            for feature in their_features
        )
        
        # Calculate final score
        total_score = our_score + their_score
        if total_score == 0:
            return 0.5
        
        score_diff = our_score - their_score
        return max(0.0, min(1.0, score_diff / total_score + 0.5))

    def calculate_market_presence_score(
        self,
        product: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> float:
        """Calculate market presence score using configured weights."""
        market_share = product.get('market_share', 0.0)
        growth_rate = product.get('growth_rate', 0.0)
        brand_recognition = product.get('brand_recognition', 0.0)
        
        # Get market data with defaults
        leader_share = market_data.get('leader_share', 100)
        avg_growth = market_data.get('avg_growth', 10)
        
        # Normalize metrics
        normalized_share = min(1.0, market_share / leader_share)
        normalized_growth = min(1.0, growth_rate / avg_growth)
        normalized_brand = min(1.0, brand_recognition / 100)
        
        # Apply configured weights
        share_weight = self.market_presence.get('share_weight', 0.4)
        growth_weight = self.market_presence.get('growth_weight', 0.4)
        brand_weight = self.market_presence.get('brand_weight', 0.2)
        
        return (
            normalized_share * share_weight +
            normalized_growth * growth_weight +
            normalized_brand * brand_weight
        )

    def calculate_customer_sentiment_score(
        self,
        product: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> float:
        """Calculate customer sentiment score with time-based weighting."""
        reviews = customer_data.get('reviews', [])
        if not reviews:
            return 0.5
        
        min_reviews = self.sentiment.get('min_reviews', 3)
        if len(reviews) < min_reviews:
            msg = f"Insufficient reviews: {len(reviews)}"
            self.logger.warning(msg)
            return 0.5
        
        # Calculate time-weighted sentiment scores
        now = datetime.now()
        weighted_scores = []
        max_age = self.sentiment.get('max_review_age_days', 180)
        recent_weight = self.sentiment.get('recent_review_weight', 1.0)
        old_weight = self.sentiment.get('old_review_weight', 0.5)
        
        for review in reviews:
            date_str = review.get('date', now.isoformat())
            review_date = datetime.fromisoformat(date_str)
            age_days = (now - review_date).days
            
            if age_days <= max_age:
                weight = recent_weight if age_days <= 30 else old_weight
                score = review.get('sentiment_score', 0.0)
                weighted_scores.append((score, weight))
        
        if not weighted_scores:
            return 0.5
        
        # Calculate weighted average
        total_weight = sum(weight for _, weight in weighted_scores)
        weighted_sum = sum(
            score * weight for score, weight in weighted_scores
        )
        
        return max(0.0, min(1.0, weighted_sum / total_weight))

    def determine_market_fit(
        self,
        product: Dict[str, Any],
        segment: str
    ) -> Dict[str, Any]:
        """Determine market fit using configured criteria."""
        segment_config = self.market_segments.get(segment, {})
        product_features = set(product.get('features', []))
        required = set(segment_config.get('required_features', []))
        
        # Check price point
        min_price = segment_config.get('min_price', 0)
        product_price = product.get('price', 0)
        price_fit = product_price >= min_price
        
        # Check required features
        missing_features = required - product_features
        feature_fit = len(missing_features) == 0
        
        # Check industry fit
        target_industries = set(segment_config.get('target_industries', []))
        product_industries = set(product.get('target_industries', []))
        industry_fit = bool(target_industries & product_industries)
        
        # Calculate overall fit score
        fit_score = (
            (1.0 if price_fit else 0.3) *
            (1.0 if feature_fit else 0.5) *
            (1.0 if industry_fit else 0.7)
        )
        
        return {
            'segment': segment,
            'fit_score': fit_score,
            'missing_features': list(missing_features),
            'price_fit': price_fit,
            'industry_fit': industry_fit
        }

    def generate_recommendations(
        self,
        scores: Dict[str, float],
        market_fits: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on configured thresholds."""
        recommendations = []
        
        # Feature-based recommendations
        feature_threshold = self.thresholds.get('feature_gap', 0.6)
        if scores['features'] < feature_threshold:
            recommendations.append({
                'category': 'Product Development',
                'priority': 'High',
                'recommendation': 'Address feature gaps',
                'details': [
                    'Identify and prioritize missing features',
                    'Focus on unique value propositions'
                ]
            })
        
        # Market presence recommendations
        presence_threshold = self.thresholds.get('market_presence', 0.4)
        if scores['market_presence'] < presence_threshold:
            recommendations.append({
                'category': 'Marketing',
                'priority': 'High',
                'recommendation': 'Increase market visibility',
                'details': [
                    'Enhance brand awareness campaigns',
                    'Expand market reach through partnerships'
                ]
            })
        
        # Customer sentiment recommendations
        sentiment_threshold = self.thresholds.get('customer_sentiment', 0.5)
        if scores['customer_sentiment'] < sentiment_threshold:
            recommendations.append({
                'category': 'Customer Success',
                'priority': 'High',
                'recommendation': 'Improve customer satisfaction',
                'details': [
                    'Address common customer pain points',
                    'Enhance support quality and response time'
                ]
            })
        
        # Market fit recommendations
        market_threshold = self.thresholds.get('market_fit', 0.8)
        for segment, fit_data in market_fits.items():
            if fit_data['fit_score'] < market_threshold:
                missing = ", ".join(fit_data["missing_features"])
                rec = {
                    'category': 'Market Strategy',
                    'priority': 'Medium',
                    'recommendation': f'Improve {segment} market fit',
                    'details': [
                        f'Add missing features: {missing}',
                        'Adjust pricing strategy if needed'
                    ]
                }
                recommendations.append(rec)
        
        # Sort by priority
        priority_map = {
            'High': self.priorities.get('high_threshold', 0.7),
            'Medium': self.priorities.get('medium_threshold', 0.4),
            'Low': self.priorities.get('low_threshold', 0.2)
        }
        
        return sorted(
            recommendations,
            key=lambda x: -priority_map.get(x['priority'], 0)
        )

    def _get_cache_key(self, input_data: Dict[str, Any]) -> str:
        """Generate a cache key for input data."""
        return str(hash(str(input_data)))

    def _get_cache_entry(self, key: str) -> Dict[str, Any]:
        """Get a cache entry if it exists and is valid."""
        if not self.cache or key not in self.cache:
            return None
        
        entry = self.cache[key]
        age = (datetime.now() - entry['timestamp']).seconds
        if age >= self.cache_ttl:
            return None
        
        return entry

    def _update_cache(self, key: str, result: Dict[str, Any]):
        """Update the cache with new results."""
        if self.cache is None:
            return
        
        if len(self.cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]['timestamp']
            )
            del self.cache[oldest]
        
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def _format_error(self, error: Exception) -> Dict[str, Any]:
        """Format error response with timestamp."""
        return {
            'status': 'error',
            'error': str(error),
            'metadata': {
                'timestamp': self._get_timestamp()
            }
        }

    def _log_error(self, error: Exception):
        """Log error with appropriate context."""
        msg = "Error processing expert analysis: "
        msg += str(error)
        self.logger.error(msg)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze products to make expert decisions."""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            # Check cache if enabled
            key = self._get_cache_key(input_data)
            entry = self._get_cache_entry(key)
            if entry:
                self.logger.info("Returning cached result")
                return entry['result']
            
            products = input_data['products']
            market_data = input_data['market_data']
            customer_data = input_data['customer_data']
            
            our_product = products[0]  # Assume first product is ours
            competitors = products[1:]
            
            # Calculate scores
            scores = {}
            for competitor in competitors:
                feature_score = self.calculate_feature_score(
                    our_product,
                    competitor
                )
                scores.setdefault('features', []).append(feature_score)
            
            scores['market_presence'] = self.calculate_market_presence_score(
                our_product,
                market_data
            )
            
            scores['customer_sentiment'] = self.calculate_customer_sentiment_score(
                our_product,
                customer_data
            )
            
            # Calculate average feature score
            scores['features'] = (
                np.mean(scores['features']) if scores['features'] else 0.5
            )
            
            # Determine market fit
            market_fits = {}
            for segment in self.market_segments:
                market_fits[segment] = self.determine_market_fit(
                    our_product,
                    segment
                )
            
            # Generate recommendations
            recommendations = self.generate_recommendations(
                scores,
                market_fits
            )
            
            # Calculate overall score
            overall_score = sum(
                score * self.weights.get(metric, 0.1)
                for metric, score in scores.items()
            )
            
            timestamp = self._get_timestamp()
            result = {
                'status': 'success',
                'data': {
                    'scores': scores,
                    'market_fits': market_fits,
                    'recommendations': recommendations,
                    'overall_score': overall_score
                },
                'metadata': {
                    'products_analyzed': len(products),
                    'timestamp': timestamp
                }
            }
            
            # Update cache if enabled
            self._update_cache(key, result)
            
            return result
            
        except Exception as e:
            self._log_error(e)
            return self._format_error(e)


if __name__ == "__main__":
    # Test the expert system agent
    agent = ExpertSystemAgent()
    
    test_data = {
        'products': [
            {
                'name': 'Our Product',
                'features': ['security', 'api_access', 'scalability'],
                'market_share': 15.0,
                'growth_rate': 25.0,
                'brand_recognition': 70.0,
                'price': 500,
                'target_industries': ['technology', 'finance']
            },
            {
                'name': 'Competitor A',
                'features': ['security', 'compliance', 'support_sla'],
                'market_share': 30.0,
                'growth_rate': 15.0,
                'brand_recognition': 90.0,
                'price': 1000,
                'target_industries': ['finance', 'healthcare']
            }
        ],
        'market_data': {
            'leader_share': 35.0,
            'avg_growth': 20.0,
            'market_size': 1000000000,
            'year_over_year_growth': 15.0
        },
        'customer_data': {
            'reviews': [
                {
                    'sentiment_score': 0.8,
                    'text': 'Great security features and API integration',
                    'date': '2023-01-01T00:00:00'
                },
                {
                    'sentiment_score': 0.6,
                    'text': 'Good product but needs better documentation',
                    'date': '2023-02-15T00:00:00'
                },
                {
                    'sentiment_score': 0.9,
                    'text': 'Excellent scalability and performance',
                    'date': '2023-03-30T00:00:00'
                }
            ]
        }
    }
    
    import asyncio
    results = asyncio.run(agent.process(test_data))
    print("Expert Analysis Results:", results['data']) 