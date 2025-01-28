import pytest
from datetime import datetime
import numpy as np
from ai_orchestration.src.expert_system import ExpertSystemAgent


@pytest.fixture
def agent():
    """Create an ExpertSystemAgent instance for testing."""
    return ExpertSystemAgent()


@pytest.fixture
def sample_data():
    """Create sample test data."""
    return {
        'products': [
            {
                'name': 'Our Product',
                'features': ['security', 'api_access', 'scalability'],
                'market_share': 15.0,
                'growth_rate': 25.0,
                'brand_recognition': 70.0,
                'price': 500
            },
            {
                'name': 'Competitor A',
                'features': ['security', 'compliance', 'support_sla'],
                'market_share': 30.0,
                'growth_rate': 15.0,
                'brand_recognition': 90.0,
                'price': 1000
            }
        ],
        'market_data': {
            'leader_share': 35.0,
            'avg_growth': 20.0
        },
        'customer_data': {
            'reviews': [
                {'sentiment_score': 0.8},
                {'sentiment_score': 0.6},
                {'sentiment_score': 0.9}
            ]
        }
    }


def test_validate_input(agent, sample_data):
    """Test input validation."""
    assert agent.validate_input(sample_data) is True
    
    # Test with missing fields
    invalid_data = {'products': []}
    assert agent.validate_input(invalid_data) is False


def test_calculate_feature_score(agent):
    """Test feature comparison scoring."""
    product1 = {'features': ['a', 'b', 'c']}
    product2 = {'features': ['b', 'c', 'd']}
    
    score = agent.calculate_feature_score(product1, product2)
    assert 0 <= score <= 1
    
    # Test with identical features
    identical = {'features': ['a', 'b', 'c']}
    score = agent.calculate_feature_score(identical, identical)
    assert score == 0.5  # Neutral score for identical features


def test_calculate_market_presence_score(agent):
    """Test market presence scoring."""
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


def test_calculate_customer_sentiment_score(agent):
    """Test customer sentiment scoring."""
    customer_data = {
        'reviews': [
            {'sentiment_score': 0.8},
            {'sentiment_score': 0.6}
        ]
    }
    
    score = agent.calculate_customer_sentiment_score({}, customer_data)
    assert 0 <= score <= 1
    
    # Test with no reviews
    empty_data = {'reviews': []}
    score = agent.calculate_customer_sentiment_score({}, empty_data)
    assert score == 0.5  # Neutral score for no data


def test_determine_market_fit(agent):
    """Test market fit determination."""
    product = {
        'features': ['security', 'compliance', 'scalability', 'support_sla'],
        'price': 1200
    }
    
    # Test enterprise segment
    fit = agent.determine_market_fit(product, 'enterprise')
    assert fit['fit_score'] == 1.0  # Perfect fit
    assert len(fit['missing_features']) == 0
    assert fit['price_fit'] is True
    
    # Test with missing features
    product['features'] = ['security']
    fit = agent.determine_market_fit(product, 'enterprise')
    assert fit['fit_score'] < 1.0
    assert len(fit['missing_features']) > 0


def test_generate_recommendations(agent):
    """Test recommendation generation."""
    scores = {
        'features': 0.4,
        'market_presence': 0.3,
        'customer_sentiment': 0.6
    }
    market_fits = {
        'enterprise': {
            'fit_score': 0.7,
            'missing_features': ['compliance'],
            'price_fit': True
        }
    }
    
    recommendations = agent.generate_recommendations(scores, market_fits)
    assert len(recommendations) > 0
    assert all(r['priority'] in ['High', 'Medium', 'Low'] for r in recommendations)
    assert recommendations[0]['priority'] == 'High'  # First should be highest priority


@pytest.mark.asyncio
async def test_process(agent, sample_data):
    """Test the complete processing pipeline."""
    result = await agent.process(sample_data)
    
    assert result['status'] == 'success'
    assert 'data' in result
    assert 'metadata' in result
    
    data = result['data']
    assert all(key in data for key in ['scores', 'market_fits', 'recommendations', 'overall_score'])
    assert 0 <= data['overall_score'] <= 1
    
    # Test with invalid data
    with pytest.raises(ValueError):
        await agent.process({'invalid': 'data'})


def test_weights_configuration(agent):
    """Test agent configuration with custom weights."""
    custom_weights = {
        'features': 0.4,
        'market_presence': 0.3,
        'customer_sentiment': 0.3
    }
    custom_agent = ExpertSystemAgent({'weights': custom_weights})
    assert custom_agent.weights['features'] == 0.4
    
    # Test with default weights when not provided
    default_agent = ExpertSystemAgent()
    assert all(w in default_agent.weights for w in ['features', 'market_presence', 'customer_sentiment']) 