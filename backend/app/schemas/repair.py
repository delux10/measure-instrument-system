from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class RepairCreate(BaseModel):
    instrument_id: int
    fault_description: Optional[str] = None
    repair_content: Optional[str] = None
    cost: Optional[float] = None
    repair_party: Optional[str] = None
    repair_date: Optional[date] = None
    operator: Optional[str] = None
    remark: Optional[str] = None


class RepairUpdate(BaseModel):
    fault_description: Optional[str] = None
    repair_content: Optional[str] = None
    cost: Optional[float] = None
    repair_party: Optional[str] = None
    repair_date: Optional[date] = None
    operator: Optional[str] = None
    remark: Optional[str] = None


class RepairResponse(BaseModel):
    id: int
    instrument_id: int
    fault_description: Optional[str] = None
    repair_content: Optional[str] = None
    cost: Optional[float] = None
    repair_party: Optional[str] = None
    repair_date: Optional[date] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
