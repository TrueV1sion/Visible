from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.name == name).first()

    # You can add more specific methods here if needed, for example:
    # def get_multi_by_business_model(
    #     self, db: Session, *, business_model: str, skip: int = 0, limit: int = 100
    # ) -> List[Customer]:
    #     return (
    #         db.query(self.model)
    #         .filter(self.model.business_model == business_model)
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

# Create a global instance of the CRUDCustomer class for easy import in API routes
customer = CRUDCustomer(Customer)
