import pytest
from datetime import datetime, timedelta
from ai_orchestration.src.expert_system import ExpertSystemAgent


@pytest.fixture
def agent():
    """Create an ExpertSystemAgent instance with caching enabled."""
    config = {
        'cache': {
            'enabled': True,
            'ttl': 60,  # 1 minute
            'max_size': 2
        }
    }
    return ExpertSystemAgent(config_path=None)


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
            'avg_growth': 20.0
        },
        'customer_data': {
            'reviews': [
                {
                    'sentiment_score': 0.8,
                    'text': 'Great security features',
                    'date': '2023-01-01T00:00:00'
                }
            ]
        }
    }


def test_cache_key_generation(agent, sample_data):
    """Test cache key generation is consistent."""
    key1 = agent._get_cache_key(sample_data)
    key2 = agent._get_cache_key(sample_data)
    assert key1 == key2


def test_cache_entry_validation(agent, sample_data):
    """Test cache entry validation."""
    key = agent._get_cache_key(sample_data)
    
    # Test with valid entry
    agent.cache[key] = {
        'result': {'status': 'success'},
        'timestamp': datetime.now()
    }
    entry = agent._get_cache_entry(key)
    assert entry is not None
    assert entry['result']['status'] == 'success'
    
    # Test with expired entry
    agent.cache[key] = {
        'result': {'status': 'success'},
        'timestamp': datetime.now() - timedelta(seconds=61)
    }
    entry = agent._get_cache_entry(key)
    assert entry is None


def test_cache_size_limit(agent, sample_data):
    """Test cache size limit enforcement."""
    # Create three different inputs
    inputs = [
        sample_data,
        {**sample_data, 'test_id': 1},
        {**sample_data, 'test_id': 2}
    ]
    
    # Add entries to cache
    for data in inputs:
        key = agent._get_cache_key(data)
        agent._update_cache(key, {'status': 'success'})
    
    # Verify cache size doesn't exceed limit
    assert len(agent.cache) <= agent.cache_max_size


@pytest.mark.asyncio
async def test_cache_hit(agent, sample_data):
    """Test cache hit returns cached result."""
    # First call to populate cache
    result1 = await agent.process(sample_data)
    assert result1['status'] == 'success'
    
    # Second call should return cached result
    result2 = await agent.process(sample_data)
    assert result2 == result1


@pytest.mark.asyncio
async def test_cache_miss(agent, sample_data):
    """Test cache miss processes new result."""
    # First call with original data
    result1 = await agent.process(sample_data)
    
    # Second call with modified data
    modified_data = {**sample_data}
    modified_data['products'][0]['market_share'] = 20.0
    result2 = await agent.process(modified_data)
    
    assert result2 != result1


@pytest.mark.asyncio
async def test_cache_expiration(agent, sample_data, monkeypatch):
    """Test cache entry expiration."""
    # First call to populate cache
    result1 = await agent.process(sample_data)
    
    # Mock time advancement
    future_time = datetime.now() + timedelta(seconds=61)
    monkeypatch.setattr(
        'ai_orchestration.src.expert_system.datetime',
        type('MockDatetime', (), {'now': lambda: future_time})
    )
    
    # Second call should process new result
    result2 = await agent.process(sample_data)
    assert result2['metadata']['timestamp'] != result1['metadata']['timestamp']


def test_cache_disabled(sample_data):
    """Test agent works correctly with cache disabled."""
    config = {'cache': {'enabled': False}}
    agent = ExpertSystemAgent(config_path=None)
    
    # Verify cache is not initialized
    assert agent.cache is None
    
    # Verify cache-related methods handle disabled cache
    key = agent._get_cache_key(sample_data)
    assert agent._get_cache_entry(key) is None
    
    # Verify update doesn't raise error
    agent._update_cache(key, {'status': 'success'})  # Should do nothing 