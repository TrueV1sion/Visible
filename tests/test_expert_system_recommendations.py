import pytest
from ai_orchestration.src.expert_system import ExpertSystemAgent


@pytest.fixture
def agent():
    """Create an ExpertSystemAgent instance."""
    return ExpertSystemAgent()


@pytest.fixture
def feature_gap_data():
    """Create test data with feature gaps."""
    return {
        'products': [
            {
                'name': 'Our Product',
                'features': ['security', 'api_access'],
                'market_share': 15.0,
                'growth_rate': 25.0,
                'brand_recognition': 70.0,
                'price': 500,
                'target_industries': ['technology']
            },
            {
                'name': 'Competitor A',
                'features': [
                    'security',
                    'api_access',
                    'compliance',
                    'support_sla',
                    'analytics'
                ],
                'market_share': 30.0,
                'growth_rate': 15.0,
                'brand_recognition': 90.0,
                'price': 1000,
                'target_industries': ['finance', 'healthcare']
            }
        ],
        'market_data': {
            'leader_share': 35.0,
            'avg_growth': 20.0
        },
        'customer_data': {
            'reviews': [
                {
                    'sentiment_score': 0.7,
                    'text': 'Good but limited features',
                    'date': '2023-01-01T00:00:00'
                }
            ]
        }
    }


@pytest.fixture
def market_presence_data():
    """Create test data with low market presence."""
    return {
        'products': [
            {
                'name': 'Our Product',
                'features': ['security', 'api_access', 'scalability'],
                'market_share': 5.0,
                'growth_rate': 10.0,
                'brand_recognition': 30.0,
                'price': 500,
                'target_industries': ['technology']
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
                    'text': 'Great product',
                    'date': '2023-01-01T00:00:00'
                }
            ]
        }
    }


@pytest.fixture
def sentiment_data():
    """Create test data with low customer sentiment."""
    return {
        'products': [
            {
                'name': 'Our Product',
                'features': ['security', 'api_access', 'scalability'],
                'market_share': 15.0,
                'growth_rate': 25.0,
                'brand_recognition': 70.0,
                'price': 500,
                'target_industries': ['technology']
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
                    'sentiment_score': 0.3,
                    'text': 'Poor support and documentation',
                    'date': '2023-01-01T00:00:00'
                },
                {
                    'sentiment_score': 0.4,
                    'text': 'Difficult to use',
                    'date': '2023-02-01T00:00:00'
                }
            ]
        }
    }


@pytest.fixture
def market_fit_data():
    """Create test data with poor market fit."""
    return {
        'products': [
            {
                'name': 'Our Product',
                'features': ['api_access', 'basic_security'],
                'market_share': 15.0,
                'growth_rate': 25.0,
                'brand_recognition': 70.0,
                'price': 500,
                'target_industries': ['technology']
            },
            {
                'name': 'Competitor A',
                'features': [
                    'security',
                    'compliance',
                    'scalability',
                    'support_sla'
                ],
                'market_share': 30.0,
                'growth_rate': 15.0,
                'brand_recognition': 90.0,
                'price': 1000,
                'target_industries': ['finance', 'healthcare']
            }
        ],
        'market_data': {
            'leader_share': 35.0,
            'avg_growth': 20.0
        },
        'customer_data': {
            'reviews': [
                {
                    'sentiment_score': 0.7,
                    'text': 'Good for small projects',
                    'date': '2023-01-01T00:00:00'
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_feature_gap_recommendations(agent, feature_gap_data):
    """Test recommendations for feature gaps."""
    result = await agent.process(feature_gap_data)
    recommendations = result['data']['recommendations']
    
    # Find feature-related recommendations
    feature_recs = [
        r for r in recommendations
        if r['category'] == 'Product Development'
    ]
    
    assert len(feature_recs) > 0
    assert feature_recs[0]['priority'] == 'High'
    assert 'feature' in feature_recs[0]['recommendation'].lower()


@pytest.mark.asyncio
async def test_market_presence_recommendations(agent, market_presence_data):
    """Test recommendations for low market presence."""
    result = await agent.process(market_presence_data)
    recommendations = result['data']['recommendations']
    
    # Find market presence recommendations
    market_recs = [
        r for r in recommendations
        if r['category'] == 'Marketing'
    ]
    
    assert len(market_recs) > 0
    assert market_recs[0]['priority'] == 'High'
    assert 'market' in market_recs[0]['recommendation'].lower()


@pytest.mark.asyncio
async def test_sentiment_recommendations(agent, sentiment_data):
    """Test recommendations for low customer sentiment."""
    result = await agent.process(sentiment_data)
    recommendations = result['data']['recommendations']
    
    # Find sentiment-related recommendations
    sentiment_recs = [
        r for r in recommendations
        if r['category'] == 'Customer Success'
    ]
    
    assert len(sentiment_recs) > 0
    assert sentiment_recs[0]['priority'] == 'High'
    assert 'satisfaction' in sentiment_recs[0]['recommendation'].lower()


@pytest.mark.asyncio
async def test_market_fit_recommendations(agent, market_fit_data):
    """Test recommendations for poor market fit."""
    result = await agent.process(market_fit_data)
    recommendations = result['data']['recommendations']
    
    # Find market fit recommendations
    fit_recs = [
        r for r in recommendations
        if r['category'] == 'Market Strategy'
    ]
    
    assert len(fit_recs) > 0
    assert 'market fit' in fit_recs[0]['recommendation'].lower()
    assert len(fit_recs[0]['details']) > 0


@pytest.mark.asyncio
async def test_recommendation_priority_sorting(agent, feature_gap_data):
    """Test recommendations are sorted by priority."""
    result = await agent.process(feature_gap_data)
    recommendations = result['data']['recommendations']
    
    # Verify high priority recommendations come first
    priorities = [r['priority'] for r in recommendations]
    high_priority_indices = [
        i for i, p in enumerate(priorities) if p == 'High'
    ]
    medium_priority_indices = [
        i for i, p in enumerate(priorities) if p == 'Medium'
    ]
    
    if high_priority_indices and medium_priority_indices:
        assert min(high_priority_indices) < min(medium_priority_indices)


@pytest.mark.asyncio
async def test_recommendation_details(agent, feature_gap_data):
    """Test recommendation details are provided."""
    result = await agent.process(feature_gap_data)
    recommendations = result['data']['recommendations']
    
    for rec in recommendations:
        assert 'category' in rec
        assert 'priority' in rec
        assert 'recommendation' in rec
        assert 'details' in rec
        assert len(rec['details']) > 0 