from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class BattlecardBase(BaseModel):
    title: str
    description: Optional[str] = None
    company_overview: Optional[str] = None
    target_market: Optional[str] = None
    competitive_analysis: Optional[Dict[str, Any]] = None
    product_features: Optional[Dict[str, Any]] = None
    pricing_structure: Optional[Dict[str, Any]] = None
    use_cases: Optional[List[Dict[str, Any]]] = None
    objection_handling: Optional[Dict[str, Any]] = None


class BattlecardCreate(BattlecardBase):
    pass


class BattlecardUpdate(BattlecardBase):
    pass


class BattlecardVersion(BaseModel):
    id: int
    version_number: int
    content: Dict[str, Any]
    created_at: datetime
    created_by_id: int

    class Config:
        from_attributes = True


class Battlecard(BattlecardBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    last_modified_by_id: Optional[int] = None
    versions: List[BattlecardVersion] = []

    class Config:
        from_attributes = True 