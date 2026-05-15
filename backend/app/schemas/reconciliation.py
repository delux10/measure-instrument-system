from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ReconciliationDiffResponse(BaseModel):
    id: int
    contract_id: int
    execution_record_id: Optional[int] = None
    diff_type: str
    contract_value: Optional[str] = None
    actual_value: Optional[str] = None
    diff_value: Optional[str] = None
    status: str
    remark: Optional[str] = None
    confirmed_by: Optional[int] = None
    confirmed_at: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReconciliationDiffUpdate(BaseModel):
    status: Optional[str] = None
    remark: Optional[str] = None
