from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock, patch
from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash


@pytest.fixture
def mock_ai_agent():
    """Create a mock AI agent."""
    mock = AsyncMock()
    mock.process.return_value = {
        "result": "Mock analysis result",
        "confidence": 0.95
    }
    return mock


@pytest.fixture
def mock_factory(mock_ai_agent):
    """Create a mock AI factory."""
    with patch("app.ai.factory.AIAgentFactory.get_agent") as mock_get:
        mock_get.return_value = mock_ai_agent
        yield mock_get


def test_list_agents(client: TestClient, admin_token_headers: dict):
    """Test listing available AI agents."""
    response = client.get(
        f"{settings.API_V1_STR}/ai/agents",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "available_agents" in content
    assert isinstance(content["available_agents"], list)


def test_process_with_agent(
    client: TestClient,
    admin_token_headers: dict,
    mock_factory,
    mock_ai_agent
):
    """Test processing data with an AI agent."""
    input_data = {
        "content": "Test content",
        "content_type": "company_overview"
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/content_analysis/process",
        headers=admin_token_headers,
        json=input_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content == mock_ai_agent.process.return_value
    mock_ai_agent.process.assert_called_once_with(input_data)


def test_analyze_competitor(
    client: TestClient,
    admin_token_headers: dict,
    mock_factory,
    mock_ai_agent
):
    """Test competitor analysis endpoint."""
    input_data = {
        "competitor_name": "Test Competitor",
        "data_points": {"feature1": "value1"}
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/competitive-analysis",
        headers=admin_token_headers,
        json=input_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content == mock_ai_agent.process.return_value
    mock_ai_agent.process.assert_called_once_with(input_data)


def test_handle_objection(
    client: TestClient,
    admin_token_headers: dict,
    mock_factory,
    mock_ai_agent
):
    """Test objection handling endpoint."""
    input_data = {
        "objection": "Price is too high",
        "context": {"product": "Enterprise Plan"}
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/objection-handling",
        headers=admin_token_headers,
        json=input_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content == mock_ai_agent.process.return_value
    mock_ai_agent.process.assert_called_once_with(input_data)


def test_generate_use_case(
    client: TestClient,
    admin_token_headers: dict,
    mock_factory,
    mock_ai_agent
):
    """Test use case generation endpoint."""
    input_data = {
        "customer_data": {"name": "Test Customer"},
        "solution_details": {"product": "Enterprise Plan"}
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/use-case",
        headers=admin_token_headers,
        json=input_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content == mock_ai_agent.process.return_value
    mock_ai_agent.process.assert_called_once_with(input_data)


def test_analyze_content(
    client: TestClient,
    admin_token_headers: dict,
    mock_factory,
    mock_ai_agent
):
    """Test content analysis endpoint."""
    input_data = {
        "content": "Test content for analysis",
        "content_type": "product_description"
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/analyze-content",
        headers=admin_token_headers,
        json=input_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content == mock_ai_agent.process.return_value
    mock_ai_agent.process.assert_called_once_with(input_data)


def test_unauthorized_access(client: TestClient):
    """Test unauthorized access to AI endpoints."""
    response = client.get(f"{settings.API_V1_STR}/ai/agents")
    assert response.status_code == 401


def test_use_case_permission(
    client: TestClient,
    db: TestClient,
    mock_factory
):
    """Test use case generation requires proper permissions."""
    # Create viewer user
    viewer_data = {
        "email": "viewer@example.com",
        "password": "viewer123",
        "full_name": "Viewer User",
        "role": UserRole.VIEWER
    }
    viewer = User(
        email=viewer_data["email"],
        hashed_password=get_password_hash(viewer_data["password"]),
        full_name=viewer_data["full_name"],
        role=viewer_data["role"]
    )
    db.add(viewer)
    db.commit()

    # Get viewer token
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": viewer_data["email"],
            "password": viewer_data["password"]
        }
    )
    tokens = response.json()
    viewer_headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }

    # Try to generate use case
    input_data = {
        "customer_data": {"name": "Test Customer"},
        "solution_details": {"product": "Enterprise Plan"}
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/use-case",
        headers=viewer_headers,
        json=input_data
    )
    assert response.status_code == 403 