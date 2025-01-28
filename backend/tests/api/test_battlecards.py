from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.battlecard import Battlecard
from app.core.security import get_password_hash


@pytest.fixture
def admin_token_headers(client: TestClient, db: Session) -> dict:
    """Create admin user and get token"""
    admin_data = {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": UserRole.ADMIN
    }
    admin = User(
        email=admin_data["email"],
        hashed_password=get_password_hash(admin_data["password"]),
        full_name=admin_data["full_name"],
        role=admin_data["role"]
    )
    db.add(admin)
    db.commit()

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": admin_data["email"],
            "password": admin_data["password"]
        }
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_create_battlecard(client: TestClient, admin_token_headers: dict):
    battlecard_data = {
        "title": "Test Battlecard",
        "description": "Test Description",
        "company_overview": "Test Company Overview",
        "target_market": "Test Target Market",
        "competitive_analysis": {"competitor1": "analysis1"},
        "product_features": {"feature1": "description1"},
        "pricing_structure": {"tier1": "price1"},
        "use_cases": [{"case1": "description1"}],
        "objection_handling": {"objection1": "response1"}
    }
    response = client.post(
        f"{settings.API_V1_STR}/battlecards/",
        headers=admin_token_headers,
        json=battlecard_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == battlecard_data["title"]
    assert "id" in content
    assert "created_at" in content


def test_read_battlecard(
    client: TestClient,
    admin_token_headers: dict,
    db: Session
):
    # Create test battlecard
    battlecard = Battlecard(
        title="Test Battlecard",
        description="Test Description",
        created_by_id=1
    )
    db.add(battlecard)
    db.commit()
    db.refresh(battlecard)

    response = client.get(
        f"{settings.API_V1_STR}/battlecards/{battlecard.id}",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == battlecard.title
    assert content["id"] == battlecard.id


def test_update_battlecard(
    client: TestClient,
    admin_token_headers: dict,
    db: Session
):
    # Create test battlecard
    battlecard = Battlecard(
        title="Test Battlecard",
        description="Test Description",
        created_by_id=1
    )
    db.add(battlecard)
    db.commit()
    db.refresh(battlecard)

    updated_data = {
        "title": "Updated Battlecard",
        "description": "Updated Description"
    }
    response = client.put(
        f"{settings.API_V1_STR}/battlecards/{battlecard.id}",
        headers=admin_token_headers,
        json=updated_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == updated_data["title"]
    assert content["description"] == updated_data["description"]


def test_delete_battlecard(
    client: TestClient,
    admin_token_headers: dict,
    db: Session
):
    # Create test battlecard
    battlecard = Battlecard(
        title="Test Battlecard",
        description="Test Description",
        created_by_id=1
    )
    db.add(battlecard)
    db.commit()
    db.refresh(battlecard)

    response = client.delete(
        f"{settings.API_V1_STR}/battlecards/{battlecard.id}",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    
    # Verify deletion
    deleted_battlecard = db.query(Battlecard).filter(
        Battlecard.id == battlecard.id
    ).first()
    assert deleted_battlecard is None 