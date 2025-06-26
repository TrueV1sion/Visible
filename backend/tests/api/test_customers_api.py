from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # Though not directly used, good for type hints if needed
from app.core.config import settings # To get API prefix
from app.schemas.customer import CustomerCreate, CustomerUpdate, QualityScore, VendorDetail

# Sample data for testing - can be shared or redefined if more specific API test data is needed
def get_api_customer_create_data(name_suffix: str = "") -> dict:
    return {
        "name": f"APITest Payer {name_suffix}",
        "description": "An API test health plan.",
        "business_model": "PPO",
        "membership_count": 250000,
        "website_url": "http://apitestpayer.com",
        "primary_contact_name": "Jane API",
        "primary_contact_email": "jane.api@apitestpayer.com",
        "notes": "API test notes.",
        "quality_scores": [
            {"metric_name": "API Overall Rating", "score": 3.5, "year": 2023, "source": "API-TestCMS"}
        ],
        "known_vendors": [
            {"name": "Vendor API-A", "service_provided": "API Claims Processing"}
        ]
    }

API_V1_STR = settings.API_V1_STR # Usually "/api/v1"

def test_create_customer_api(client: TestClient, db: Session) -> None: # db fixture to ensure clean DB
    customer_data = get_api_customer_create_data("CreateAPI")
    response = client.post(f"{API_V1_STR}/customers/", json=customer_data)

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == customer_data["name"]
    assert content["description"] == customer_data["description"]
    assert "id" in content
    assert len(content["quality_scores"]) == 1
    assert content["quality_scores"][0]["metric_name"] == "API Overall Rating"

def test_create_customer_api_duplicate_name(client: TestClient, db: Session) -> None:
    customer_data = get_api_customer_create_data("DuplicateAPI")
    client.post(f"{API_V1_STR}/customers/", json=customer_data) # Create first customer

    response = client.post(f"{API_V1_STR}/customers/", json=customer_data) # Attempt to create duplicate
    assert response.status_code == 400 # As per our endpoint logic
    content = response.json()
    assert "detail" in content
    assert "already exists" in content["detail"]


def test_read_customer_api(client: TestClient, db: Session) -> None:
    customer_data = get_api_customer_create_data("ReadAPI")
    response_create = client.post(f"{API_V1_STR}/customers/", json=customer_data)
    customer_id = response_create.json()["id"]

    response_read = client.get(f"{API_V1_STR}/customers/{customer_id}")
    assert response_read.status_code == 200
    content = response_read.json()
    assert content["id"] == customer_id
    assert content["name"] == customer_data["name"]

def test_read_non_existent_customer_api(client: TestClient, db: Session) -> None:
    response = client.get(f"{API_V1_STR}/customers/999999") # Non-existent ID
    assert response.status_code == 404

def test_read_customers_api(client: TestClient, db: Session) -> None:
    customer_data1 = get_api_customer_create_data("ListAPI1")
    customer_data2 = get_api_customer_create_data("ListAPI2")
    client.post(f"{API_V1_STR}/customers/", json=customer_data1)
    client.post(f"{API_V1_STR}/customers/", json=customer_data2)

    response = client.get(f"{API_V1_STR}/customers/?skip=0&limit=10")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 2 # Could be more from other tests if DB wasn't fully isolated per test func
                            # but our fixture handles this.
    retrieved_names = [c["name"] for c in content]
    assert customer_data1["name"] in retrieved_names
    assert customer_data2["name"] in retrieved_names

def test_update_customer_api(client: TestClient, db: Session) -> None:
    customer_data = get_api_customer_create_data("UpdateAPI")
    response_create = client.post(f"{API_V1_STR}/customers/", json=customer_data)
    customer_id = response_create.json()["id"]

    update_data = {
        "description": "Updated via API",
        "membership_count": 300000,
        "quality_scores": [ # Completely replace quality scores
            {"metric_name": "Updated API Rating", "score": 4.8, "year": 2024, "source": "API-TestCMS-Updated"}
        ]
    }
    response_update = client.put(f"{API_V1_STR}/customers/{customer_id}", json=update_data)
    assert response_update.status_code == 200
    content = response_update.json()
    assert content["id"] == customer_id
    assert content["description"] == update_data["description"]
    assert content["membership_count"] == update_data["membership_count"]
    assert content["name"] == customer_data["name"] # Name not updated
    assert len(content["quality_scores"]) == 1
    assert content["quality_scores"][0]["metric_name"] == "Updated API Rating"

def test_update_non_existent_customer_api(client: TestClient, db: Session) -> None:
    update_data = {"description": "Trying to update non-existent"}
    response = client.put(f"{API_V1_STR}/customers/999999", json=update_data)
    assert response.status_code == 404

def test_delete_customer_api(client: TestClient, db: Session) -> None:
    customer_data = get_api_customer_create_data("DeleteAPI")
    response_create = client.post(f"{API_V1_STR}/customers/", json=customer_data)
    customer_id = response_create.json()["id"]

    response_delete = client.delete(f"{API_V1_STR}/customers/{customer_id}")
    assert response_delete.status_code == 200
    content_deleted = response_delete.json()
    assert content_deleted["id"] == customer_id # Endpoint returns deleted object

    response_get_after_delete = client.get(f"{API_V1_STR}/customers/{customer_id}")
    assert response_get_after_delete.status_code == 404

def test_delete_non_existent_customer_api(client: TestClient, db: Session) -> None:
    response = client.delete(f"{API_V1_STR}/customers/999999")
    assert response.status_code == 404
