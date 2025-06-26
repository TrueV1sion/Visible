import pytest
from sqlalchemy.orm import Session

from app import crud
from app.schemas.customer import CustomerCreate, CustomerUpdate, VendorDetail, QualityScore
from app.models.customer import Customer as CustomerModel # Alias to avoid confusion

# Sample data for testing
def get_customer_create_data(name_suffix: str = "") -> CustomerCreate:
    return CustomerCreate(
        name=f"Test Payer {name_suffix}",
        description="A test health plan for CRUD operations.",
        business_model="HMO",
        membership_count=100000,
        website_url="http://testpayer.com",
        primary_contact_name="John Doe",
        primary_contact_email="john.doe@testpayer.com",
        notes="Initial notes.",
        quality_scores=[
            QualityScore(metric_name="Overall Rating", score=4.0, year=2023, source="TestCMS")
        ],
        known_vendors=[
            VendorDetail(name="Vendor A", service_provided="Claims Processing")
        ]
    )

def test_create_customer(db: Session) -> None:
    customer_in = get_customer_create_data("Create")
    db_customer = crud.customer.create(db=db, obj_in=customer_in)

    assert db_customer is not None
    assert db_customer.name == customer_in.name
    assert db_customer.description == customer_in.description
    assert db_customer.business_model == customer_in.business_model
    assert db_customer.membership_count == customer_in.membership_count
    assert db_customer.website_url == str(customer_in.website_url) # Pydantic model stores HttpUrl
    assert db_customer.id is not None
    assert len(db_customer.quality_scores) == 1
    assert db_customer.quality_scores[0]["metric_name"] == "Overall Rating"
    assert len(db_customer.known_vendors) == 1
    assert db_customer.known_vendors[0]["name"] == "Vendor A"

def test_get_customer(db: Session) -> None:
    customer_in = get_customer_create_data("Get")
    db_customer_created = crud.customer.create(db=db, obj_in=customer_in)

    db_customer_retrieved = crud.customer.get(db=db, id=db_customer_created.id)

    assert db_customer_retrieved is not None
    assert db_customer_retrieved.id == db_customer_created.id
    assert db_customer_retrieved.name == customer_in.name

def test_get_customer_by_name(db: Session) -> None:
    customer_in = get_customer_create_data("GetByName")
    crud.customer.create(db=db, obj_in=customer_in)

    db_customer_retrieved = crud.customer.get_by_name(db=db, name=customer_in.name)
    assert db_customer_retrieved is not None
    assert db_customer_retrieved.name == customer_in.name

def test_get_multi_customers(db: Session) -> None:
    customer_in1 = get_customer_create_data("Multi1")
    customer_in2 = get_customer_create_data("Multi2")
    crud.customer.create(db=db, obj_in=customer_in1)
    crud.customer.create(db=db, obj_in=customer_in2)

    customers = crud.customer.get_multi(db=db, skip=0, limit=10)
    assert len(customers) >= 2 # Could be more if other tests ran and didn't clean up fully, but fixture should handle

    # Check if our created customers are in the list
    retrieved_names = [c.name for c in customers]
    assert customer_in1.name in retrieved_names
    assert customer_in2.name in retrieved_names

def test_update_customer(db: Session) -> None:
    customer_in = get_customer_create_data("Update")
    db_customer = crud.customer.create(db=db, obj_in=customer_in)

    updated_description = "Updated description for test."
    updated_membership = 120000
    customer_update_data = CustomerUpdate(
        description=updated_description,
        membership_count=updated_membership,
        quality_scores=[
            QualityScore(metric_name="Overall Rating", score=4.5, year=2023, source="TestCMS-Updated")
        ]
    )

    db_customer_updated = crud.customer.update(db=db, db_obj=db_customer, obj_in=customer_update_data)

    assert db_customer_updated is not None
    assert db_customer_updated.id == db_customer.id
    assert db_customer_updated.description == updated_description
    assert db_customer_updated.membership_count == updated_membership
    assert db_customer_updated.name == customer_in.name # Name wasn't updated
    assert len(db_customer_updated.quality_scores) == 1
    assert db_customer_updated.quality_scores[0]["score"] == 4.5
    assert db_customer_updated.quality_scores[0]["source"] == "TestCMS-Updated"


def test_delete_customer(db: Session) -> None:
    customer_in = get_customer_create_data("Delete")
    db_customer_created = crud.customer.create(db=db, obj_in=customer_in)

    deleted_customer = crud.customer.remove(db=db, id=db_customer_created.id)
    retrieved_after_delete = crud.customer.get(db=db, id=db_customer_created.id)

    assert deleted_customer is not None
    assert deleted_customer.id == db_customer_created.id
    assert retrieved_after_delete is None

# It's good practice to also test for non-existent cases
def test_get_non_existent_customer(db: Session) -> None:
    retrieved_customer = crud.customer.get(db=db, id=99999) # Assuming this ID won't exist
    assert retrieved_customer is None

def test_delete_non_existent_customer(db: Session) -> None:
    # Ensure it doesn't raise an error and returns None or appropriate response
    deleted_customer = crud.customer.remove(db=db, id=99999)
    assert deleted_customer is None
