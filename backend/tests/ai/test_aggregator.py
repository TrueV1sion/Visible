import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from app.ai.agents.aggregator import AggregatorOrchestrationAgent


@pytest.fixture
def agent():
    """Create an AggregatorOrchestrationAgent instance for testing."""
    return AggregatorOrchestrationAgent()


@pytest.fixture
def mock_session():
    """Create a mock aiohttp ClientSession."""
    with patch('aiohttp.ClientSession') as mock:
        yield mock


@pytest.fixture
def sample_input():
    """Create sample test input data."""
    return {
        "query": "Competitor A",
        "context": {
            "industry": "technology",
            "market_segment": "enterprise"
        }
    }


@pytest.fixture
def sample_brave_response():
    """Create sample Brave Search API response."""
    return {
        "web": [
            {
                "title": "Competitor A - Enterprise Solutions",
                "description": "Leading provider of enterprise software",
                "url": "https://example.com/competitor-a"
            },
            {
                "title": "Competitor A News",
                "description": "Recent updates about Competitor A",
                "url": "https://example.com/news"
            }
        ]
    }


@pytest.fixture
def sample_perplexity_response():
    """Create sample Perplexity API response."""
    return {
        "results": [
            {
                "content": "Analysis of Competitor A's market position",
                "confidence": 0.85
            },
            {
                "content": "Recent product launches and strategy",
                "confidence": 0.92
            }
        ]
    }


@pytest.mark.asyncio
async def test_process_valid_input(agent, sample_input):
    """Test processing with valid input data."""
    result = await agent.process(sample_input)
    assert result["status"] == "success"
    assert "data" in result
    assert result["data"]["query"] == sample_input["query"]


@pytest.mark.asyncio
async def test_process_invalid_input(agent):
    """Test processing with invalid input data."""
    with pytest.raises(ValueError):
        await agent.process({})


@pytest.mark.asyncio
async def test_fetch_from_brave_search(
    agent,
    mock_session,
    sample_brave_response
):
    """Test fetching data from Brave Search API."""
    # Mock the session's get method
    mock_get = AsyncMock()
    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=sample_brave_response
    )
    mock_session.return_value.get = mock_get

    # Set up session
    await agent.setup_session()

    # Test the fetch
    results = await agent._fetch_from_brave_search("Competitor A")
    assert len(results) == 2
    assert all(r["source"] == "brave_search" for r in results)
    assert all(r["type"] == "web_result" for r in results)


@pytest.mark.asyncio
async def test_fetch_from_perplexity(
    agent,
    mock_session,
    sample_perplexity_response
):
    """Test fetching data from Perplexity API."""
    # Mock the session's post method
    mock_post = AsyncMock()
    mock_post.return_value.__aenter__.return_value.status = 200
    mock_post.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=sample_perplexity_response
    )
    mock_session.return_value.post = mock_post

    # Set up session
    await agent.setup_session()

    # Test the fetch
    results = await agent._fetch_from_perplexity("Competitor A")
    assert len(results) == 2
    assert all(r["source"] == "perplexity" for r in results)
    assert all(r["type"] == "ai_analysis" for r in results)


@pytest.mark.asyncio
async def test_merge_results(agent):
    """Test merging and deduplicating results."""
    sample_results = [
        {
            "source": "brave_search",
            "type": "web_result",
            "url": "https://example.com/1",
            "title": "Result 1"
        },
        {
            "source": "brave_search",
            "type": "web_result",
            "url": "https://example.com/1",  # Duplicate URL
            "title": "Result 1 Duplicate"
        },
        {
            "source": "perplexity",
            "type": "ai_analysis",
            "content": "Analysis 1"
        }
    ]

    merged = agent._merge_results(sample_results)
    assert len(merged) == 2  # One duplicate removed
    assert any(r["source"] == "brave_search" for r in merged)
    assert any(r["source"] == "perplexity" for r in merged)


@pytest.mark.asyncio
async def test_calculate_confidence(agent):
    """Test confidence score calculation."""
    sample_data = [
        {
            "source": "internal_db",
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "source": "perplexity",
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "source": "social_media",
            "timestamp": datetime.utcnow().isoformat()
        }
    ]

    confidence = agent._calculate_confidence(sample_data)
    assert 0 <= confidence <= 1


@pytest.mark.asyncio
async def test_source_breakdown(agent):
    """Test source breakdown calculation."""
    sample_data = [
        {"source": "brave_search"},
        {"source": "brave_search"},
        {"source": "perplexity"},
        {"source": "internal_db"}
    ]

    breakdown = agent._get_source_breakdown(sample_data)
    assert breakdown["brave_search"] == 2
    assert breakdown["perplexity"] == 1
    assert breakdown["internal_db"] == 1


@pytest.mark.asyncio
async def test_error_handling(agent, mock_session):
    """Test error handling during data fetching."""
    # Mock a failed API call
    mock_get = AsyncMock()
    mock_get.return_value.__aenter__.return_value.status = 500
    mock_session.return_value.get = mock_get

    # Set up session
    await agent.setup_session()

    # Test error handling
    results = await agent._fetch_from_brave_search("Competitor A")
    assert results == []  # Should return empty list on error


@pytest.mark.asyncio
async def test_cleanup(agent, mock_session):
    """Test cleanup of resources."""
    # Set up session
    await agent.setup_session()
    assert agent.session is not None

    # Clean up
    await agent.cleanup()
    assert agent.session is None


@pytest.mark.asyncio
async def test_parse_unstructured_insights(agent):
    """Test parsing of unstructured insight text."""
    sample_text = """
    - Category: strategic
    - Description: Key market opportunity
    - Priority: high
    - Confidence: 0.85

    - Category: threat
    - Description: Competitive pressure
    - Priority: medium
    - Confidence: 0.75
    """

    insights = agent._parse_unstructured_insights(sample_text)
    assert len(insights) == 2
    assert insights[0]["category"] == "strategic"
    assert insights[0]["priority"] == "high"
    assert insights[1]["category"] == "threat"
    assert insights[1]["priority"] == "medium" 