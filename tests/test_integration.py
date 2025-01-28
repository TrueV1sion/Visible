import pytest
from datetime import datetime
from ai_orchestration.src.expert_system import ExpertSystemAgent
from ai_orchestration.src.quality_checker import QualityCheckerAgent
from ai_orchestration.src.contextual_tagger import ContextualTaggerAgent


@pytest.fixture
def expert_system():
    """Create ExpertSystemAgent instance."""
    return ExpertSystemAgent()


@pytest.fixture
def quality_checker():
    """Create QualityCheckerAgent instance."""
    return QualityCheckerAgent()


@pytest.fixture
def contextual_tagger():
    """Create ContextualTaggerAgent instance."""
    return ContextualTaggerAgent()


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
                'description': 'Enterprise-grade security solution with API access'
            },
            {
                'name': 'Competitor A',
                'features': ['security', 'compliance', 'support_sla'],
                'market_share': 30.0,
                'growth_rate': 15.0,
                'brand_recognition': 90.0,
                'price': 1000,
                'description': 'Industry-leading compliance and security platform'
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
                    'text': 'Great security features and API integration'
                },
                {
                    'sentiment_score': 0.6,
                    'text': 'Good product but needs better documentation'
                },
                {
                    'sentiment_score': 0.9,
                    'text': 'Excellent scalability and performance'
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_quality_checker_to_expert_system(
    quality_checker,
    expert_system,
    sample_data
):
    """Test data flow from quality checker to expert system."""
    # First run quality checks
    quality_result = await quality_checker.process(sample_data)
    assert quality_result['status'] == 'success'
    
    # If quality checks pass, proceed to expert analysis
    if quality_result['status'] == 'success':
        expert_result = await expert_system.process(sample_data)
        assert expert_result['status'] == 'success'
        assert 'recommendations' in expert_result['data']


@pytest.mark.asyncio
async def test_contextual_tagger_to_expert_system(
    contextual_tagger,
    expert_system,
    sample_data
):
    """Test data flow from contextual tagger to expert system."""
    # First run contextual tagging
    tagged_result = await contextual_tagger.process(sample_data)
    assert tagged_result['status'] == 'success'
    
    # Add tags to product descriptions
    enriched_data = sample_data.copy()
    for i, product in enumerate(enriched_data['products']):
        product['tags'] = tagged_result['data']['tags'][i]
    
    # Process enriched data with expert system
    expert_result = await expert_system.process(enriched_data)
    assert expert_result['status'] == 'success'
    assert 'recommendations' in expert_result['data']


@pytest.mark.asyncio
async def test_complete_pipeline(
    quality_checker,
    contextual_tagger,
    expert_system,
    sample_data
):
    """Test the complete analysis pipeline."""
    # Step 1: Quality Check
    quality_result = await quality_checker.process(sample_data)
    assert quality_result['status'] == 'success'
    
    # Step 2: Contextual Tagging
    if quality_result['status'] == 'success':
        tagged_result = await contextual_tagger.process(sample_data)
        assert tagged_result['status'] == 'success'
        
        # Enrich data with tags
        enriched_data = sample_data.copy()
        for i, product in enumerate(enriched_data['products']):
            product['tags'] = tagged_result['data']['tags'][i]
    
    # Step 3: Expert Analysis
    if tagged_result['status'] == 'success':
        expert_result = await expert_system.process(enriched_data)
        assert expert_result['status'] == 'success'
        
        # Verify the complete analysis
        assert 'scores' in expert_result['data']
        assert 'market_fits' in expert_result['data']
        assert 'recommendations' in expert_result['data']
        assert len(expert_result['data']['recommendations']) > 0


@pytest.mark.asyncio
async def test_error_handling(
    quality_checker,
    contextual_tagger,
    expert_system
):
    """Test error handling in the pipeline."""
    invalid_data = {'products': []}
    
    # Test quality checker error handling
    quality_result = await quality_checker.process(invalid_data)
    assert quality_result['status'] == 'error'
    
    # Test contextual tagger error handling
    tagged_result = await contextual_tagger.process(invalid_data)
    assert tagged_result['status'] == 'error'
    
    # Test expert system error handling
    with pytest.raises(ValueError):
        await expert_system.process(invalid_data)


@pytest.mark.asyncio
async def test_data_enrichment(
    quality_checker,
    contextual_tagger,
    expert_system,
    sample_data
):
    """Test data enrichment through the pipeline."""
    # Step 1: Quality Check with metadata
    quality_result = await quality_checker.process(sample_data)
    assert 'metadata' in quality_result
    
    # Add quality metrics to data
    enriched_data = sample_data.copy()
    enriched_data['quality_metrics'] = quality_result['data']['metrics']
    
    # Step 2: Contextual Tagging with enhanced data
    tagged_result = await contextual_tagger.process(enriched_data)
    assert 'metadata' in tagged_result
    
    # Add tags to enriched data
    for i, product in enumerate(enriched_data['products']):
        product['tags'] = tagged_result['data']['tags'][i]
    
    # Step 3: Expert Analysis with fully enriched data
    expert_result = await expert_system.process(enriched_data)
    assert 'metadata' in expert_result
    
    # Verify data enrichment
    assert 'quality_metrics' in enriched_data
    assert 'tags' in enriched_data['products'][0]
    assert len(expert_result['data']['recommendations']) > 0 