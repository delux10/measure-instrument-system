from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class BorrowCreate(BaseModel):
    instrument_id: int
    from_department: Optional[int] = None
    to_department: Optional[int] = None
    borrower: Optional[str] = None
    expected_return_date: Optional[date] = None


class BorrowUpdate(BaseModel):
    actual_return_date: Optional[date] = None
    status: Optional[str] = None


class BorrowResponse(BaseModel):
    id: int
    instrument_id: int
    from_department: Optional[int] = None
    to_department: Optional[int] = None
    borrower: Optional[str] = None
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
