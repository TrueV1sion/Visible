import pytest
from datetime import datetime, timedelta
from ai_orchestration.src.expert_system import ExpertSystemAgent


@pytest.fixture
def agent():
    """Create an ExpertSystemAgent instance."""
    test_config = {
        'feature_weights': {
            'security': 1.2,
            'compliance': 1.1,
            'scalability': 1.0,
            'api_access': 0.9,
            'support_sla': 0.8
        },
        'market_presence': {
            'share_weight': 0.4,
            'growth_weight': 0.4,
            'brand_weight': 0.2
        },
        'sentiment': {
            'recent_review_weight': 1.0,
            'old_review_weight': 0.5,
            'min_reviews': 2,
            'max_review_age_days': 180
        }
    }
    return ExpertSystemAgent(test_config)


def test_feature_score_calculation(agent):
    """Test feature comparison score calculation."""
    our_product = {
        'features': ['security', 'api_access', 'scalability']
    }
    competitor = {
        'features': ['security', 'compliance', 'support_sla']
    }
    
    score = agent.calculate_feature_score(our_product, competitor)
    assert 0 <= score <= 1
    
    # Test with identical features
    score = agent.calculate_feature_score(our_product, our_product)
    assert score == 0.5
    
    # Test with no features
    empty = {'features': []}
    score = agent.calculate_feature_score(empty, empty)
    assert score == 0.5
    
    # Test with weighted features
    weighted_product = {
        'features': ['security', 'compliance']  # Higher weights
    }
    basic_product = {
        'features': ['api_access', 'support_sla']  # Lower weights
    }
    high_score = agent.calculate_feature_score(
        weighted_product,
        basic_product
    )
    low_score = agent.calculate_feature_score(
        basic_product,
        weighted_product
    )
    assert high_score > low_score


def test_market_presence_score_calculation(agent):
    """Test market presence score calculation."""
    product = {
        'market_share': 20.0,
        'growth_rate': 15.0,
        'brand_recognition': 80.0
    }
    market_data = {
        'leader_share': 40.0,
        'avg_growth': 10.0
    }
    
    score = agent.calculate_market_presence_score(product, market_data)
    assert 0 <= score <= 1
    
    # Test with missing data
    incomplete = {}
    score = agent.calculate_market_presence_score(
        incomplete,
        market_data
    )
    assert score >= 0
    
    # Test weight impact
    high_share = {
        'market_share': 35.0,  # High share (weight 0.4)
        'growth_rate': 5.0,    # Low growth (weight 0.4)
        'brand_recognition': 50.0  # Medium brand (weight 0.2)
    }
    high_growth = {
        'market_share': 5.0,    # Low share
        'growth_rate': 35.0,    # High growth
        'brand_recognition': 50.0  # Medium brand
    }
    
    share_score = agent.calculate_market_presence_score(
        high_share,
        market_data
    )
    growth_score = agent.calculate_market_presence_score(
        high_growth,
        market_data
    )
    assert abs(share_score - growth_score) < 0.1  # Similar due to weights


def test_customer_sentiment_score_calculation(agent):
    """Test customer sentiment score calculation."""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    recent_date = (now - timedelta(days=15)).isoformat()
    old_date = (now - timedelta(days=90)).isoformat()
    
    customer_data = {
        'reviews': [
            {
                'sentiment_score': 0.8,
                'date': recent_date
            },
            {
                'sentiment_score': 0.6,
                'date': old_date
            }
        ]
    }
    
    score = agent.calculate_customer_sentiment_score({}, customer_data)
    assert 0 <= score <= 1
    
    # Test with no reviews
    empty = {'reviews': []}
    score = agent.calculate_customer_sentiment_score({}, empty)
    assert score == 0.5
    
    # Test with insufficient reviews
    insufficient = {'reviews': [{'sentiment_score': 0.8}]}
    score = agent.calculate_customer_sentiment_score({}, insufficient)
    assert score == 0.5
    
    # Test time weighting
    recent = {
        'reviews': [
            {
                'sentiment_score': 1.0,
                'date': recent_date
            },
            {
                'sentiment_score': 0.0,
                'date': old_date
            }
        ]
    }
    old = {
        'reviews': [
            {
                'sentiment_score': 0.0,
                'date': recent_date
            },
            {
                'sentiment_score': 1.0,
                'date': old_date
            }
        ]
    }
    recent_score = agent.calculate_customer_sentiment_score({}, recent)
    old_score = agent.calculate_customer_sentiment_score({}, old)
    assert recent_score > old_score


def test_market_fit_calculation(agent):
    """Test market fit calculation."""
    product = {
        'features': [
            'security',
            'compliance',
            'scalability',
            'support_sla'
        ],
        'price': 1200,
        'target_industries': ['finance', 'healthcare']
    }
    
    # Test enterprise fit
    fit = agent.determine_market_fit(product, 'enterprise')
    assert fit['fit_score'] == 1.0
    assert len(fit['missing_features']) == 0
    assert fit['price_fit'] is True
    assert fit['industry_fit'] is True
    
    # Test with missing features
    limited = {
        'features': ['security'],
        'price': 1200,
        'target_industries': ['finance']
    }
    fit = agent.determine_market_fit(limited, 'enterprise')
    assert fit['fit_score'] < 1.0
    assert len(fit['missing_features']) > 0
    
    # Test with wrong price point
    cheap = {**product, 'price': 50}
    fit = agent.determine_market_fit(cheap, 'enterprise')
    assert fit['fit_score'] < 1.0
    assert fit['price_fit'] is False
    
    # Test with wrong industry
    wrong_industry = {**product, 'target_industries': ['retail']}
    fit = agent.determine_market_fit(wrong_industry, 'enterprise')
    assert fit['fit_score'] < 1.0
    assert fit['industry_fit'] is False


@pytest.mark.asyncio
async def test_overall_score_calculation(agent):
    """Test overall score calculation."""
    input_data = {
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
                'features': ['security', 'api_access'],
                'market_share': 30.0,
                'growth_rate': 15.0,
                'brand_recognition': 90.0,
                'price': 1000,
                'target_industries': ['finance']
            }
        ],
        'market_data': {
            'leader_share': 35.0,
            'avg_growth': 20.0
        },
        'customer_data': {
            'reviews': [
                {
                    'sentiment_score': 0.8,
                    'date': datetime.now().isoformat()
                },
                {
                    'sentiment_score': 0.6,
                    'date': (
                        datetime.now() - timedelta(days=30)
                    ).isoformat()
                }
            ]
        }
    }
    
    result = await agent.process(input_data)
    assert 'overall_score' in result['data']
    assert 0 <= result['data']['overall_score'] <= 1
    
    # Verify score components
    scores = result['data']['scores']
    assert 'features' in scores
    assert 'market_presence' in scores
    assert 'customer_sentiment' in scores
    
    # Verify each component is weighted
    weights_sum = sum(
        agent.weights.get(metric, 0.1)
        for metric in scores.keys()
    )
    assert abs(weights_sum - 1.0) < 0.1  # Should sum to ~1.0 