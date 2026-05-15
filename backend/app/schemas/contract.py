from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ContractCreate(BaseModel):
    contract_no: str
    name: Optional[str] = None
    agency_id: int
    department_id: Optional[int] = None
    contract_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: Optional[float] = None
    payment_terms: Optional[str] = None
    invoice_title: Optional[str] = None
    tax_id: Optional[str] = None
    invoice_type: Optional[str] = None
    tax_rate: Optional[float] = None
    status: str = "pending"
    remark: Optional[str] = None


class ContractUpdate(BaseModel):
    name: Optional[str] = None
    agency_id: Optional[int] = None
    department_id: Optional[int] = None
    contract_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: Optional[float] = None
    payment_terms: Optional[str] = None
    invoice_title: Optional[str] = None
    tax_id: Optional[str] = None
    invoice_type: Optional[str] = None
    tax_rate: Optional[float] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class ContractResponse(BaseModel):
    id: int
    contract_no: str
    name: Optional[str] = None
    agency_id: int
    department_id: Optional[int] = None
    contract_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: Optional[float] = None
    payment_terms: Optional[str] = None
    invoice_title: Optional[str] = None
    tax_id: Optional[str] = None
    invoice_type: Optional[str] = None
    tax_rate: Optional[float] = None
    status: str
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractVersionCreate(BaseModel):
    version_no: str
    version_label: Optional[str] = None
    remark: Optional[str] = None


class ContractVersionResponse(BaseModel):
    id: int
    contract_id: int
    version_no: str
    version_label: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    uploader_id: Optional[int] = None
    is_current: int = 0
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractItemCreate(BaseModel):
    contract_id: int
    instrument_name: str
    specification: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    remark: Optional[str] = None


class ContractItemUpdate(BaseModel):
    instrument_name: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    remark: Optional[str] = None


class ContractItemResponse(BaseModel):
    id: int
    contract_id: int
    instrument_name: str
    specification: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
