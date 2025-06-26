from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl
import datetime

class VendorDetail(BaseModel):
    name: str
    service_provided: Optional[str] = None
    notes: Optional[str] = None

class QualityScore(BaseModel):
    metric_name: str
    score: float
    year: Optional[int] = None
    source: Optional[str] = None

class CustomerBase(BaseModel):
    name: str
    description: Optional[str] = None
    business_model: Optional[str] = None # e.g., HMO, PPO, Value-Based Care
    membership_count: Optional[int] = None

    website_url: Optional[HttpUrl] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None # Add email validation if needed
    primary_contact_phone: Optional[str] = None

    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    quality_scores: Optional[List[QualityScore]] = []
    known_vendors: Optional[List[VendorDetail]] = []

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    business_model: Optional[str] = None
    membership_count: Optional[int] = None
    website_url: Optional[HttpUrl] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    notes: Optional[str] = None
    quality_scores: Optional[List[QualityScore]] = None
    known_vendors: Optional[List[VendorDetail]] = None

class Customer(CustomerBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    quality_scores: List[QualityScore] = []
    known_vendors: List[VendorDetail] = []

    class Config:
        orm_mode = True
