from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ExecutionRecordCreate(BaseModel):
    contract_item_id: Optional[int] = None
    instrument_id: Optional[int] = None
    department_id: int
    agency_id: int
    actual_date: Optional[date] = None
    actual_quantity: Optional[int] = None
    actual_unit_price: Optional[float] = None
    actual_amount: Optional[float] = None
    result: Optional[str] = None
    certificate_no: Optional[str] = None
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    payment_status: str = "unpaid"
    payment_amount: Optional[float] = 0
    payment_date: Optional[date] = None


class ExecutionRecordUpdate(BaseModel):
    contract_item_id: Optional[int] = None
    actual_date: Optional[date] = None
    actual_quantity: Optional[int] = None
    actual_unit_price: Optional[float] = None
    actual_amount: Optional[float] = None
    result: Optional[str] = None
    certificate_no: Optional[str] = None
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    payment_status: Optional[str] = None
    payment_amount: Optional[float] = None
    payment_date: Optional[date] = None


class ExecutionRecordResponse(BaseModel):
    id: int
    contract_item_id: Optional[int] = None
    instrument_id: Optional[int] = None
    department_id: int
    agency_id: int
    actual_date: Optional[date] = None
    actual_quantity: Optional[int] = None
    actual_unit_price: Optional[float] = None
    actual_amount: Optional[float] = None
    result: Optional[str] = None
    certificate_no: Optional[str] = None
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    payment_status: str
    payment_amount: Optional[float] = 0
    payment_date: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
