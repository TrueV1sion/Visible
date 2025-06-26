from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db.base import get_db # Dependency for DB session

router = APIRouter()


@router.post("/", response_model=schemas.Customer)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: schemas.CustomerCreate,
) -> Any:
    """
    Create new customer (Health Plan/Payer).
    """
    customer = crud.customer.get_by_name(db, name=customer_in.name)
    if customer:
        raise HTTPException(
            status_code=400,
            detail="A customer with this name already exists in the system.",
        )
    customer = crud.customer.create(db=db, obj_in=customer_in)
    return customer


@router.get("/", response_model=List[schemas.Customer])
def read_customers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    # Add other query parameters for filtering if needed
    # e.g., business_model: Optional[str] = Query(None, description="Filter by business model")
) -> Any:
    """
    Retrieve customers.
    """
    customers = crud.customer.get_multi(db, skip=skip, limit=limit)
    # if business_model:
    #     customers = [c for c in customers if c.business_model == business_model] # Example filtering
    return customers


@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
) -> Any:
    """
    Get customer by ID.
    """
    customer = crud.customer.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: schemas.CustomerUpdate,
) -> Any:
    """
    Update a customer.
    """
    customer = crud.customer.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if new name conflicts with an existing customer (if name is being changed)
    if customer_in.name and customer_in.name != customer.name:
        existing_customer = crud.customer.get_by_name(db, name=customer_in.name)
        if existing_customer and existing_customer.id != customer_id:
            raise HTTPException(status_code=400, detail="Another customer with this name already exists.")

    customer = crud.customer.update(db=db, db_obj=customer, obj_in=customer_in)
    return customer


@router.delete("/{customer_id}", response_model=schemas.Customer)
def delete_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
) -> Any:
    """
    Delete a customer.
    """
    customer = crud.customer.get(db=db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    # Add any pre-delete checks or related data cleanup here if necessary
    customer = crud.customer.remove(db=db, id=customer_id)
    return customer
