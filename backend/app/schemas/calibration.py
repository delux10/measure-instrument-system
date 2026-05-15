from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class CalibrationAgencyCreate(BaseModel):
    name: str
    qualification: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    service_range: Optional[str] = None
    cooperation_end: Optional[date] = None


class CalibrationAgencyResponse(BaseModel):
    id: int
    name: str
    qualification: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    service_range: Optional[str] = None
    cooperation_end: Optional[date] = None

    class Config:
        from_attributes = True


class CalibrationRecordCreate(BaseModel):
    instrument_id: int
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    agency_id: Optional[int] = None
    result: Optional[str] = None
    certificate_no: Optional[str] = None
    cost: Optional[float] = None
    contract_id: Optional[int] = None
    contract_item_id: Optional[int] = None
    operator: Optional[str] = None
    remark: Optional[str] = None


class CalibrationRecordUpdate(BaseModel):
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    agency_id: Optional[int] = None
    result: Optional[str] = None
    certificate_no: Optional[str] = None
    cost: Optional[float] = None
    contract_id: Optional[int] = None
    contract_item_id: Optional[int] = None
    operator: Optional[str] = None
    remark: Optional[str] = None


class CalibrationRecordResponse(BaseModel):
    id: int
    instrument_id: int
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    agency_id: Optional[int] = None
    result: Optional[str] = None
    certificate_no: Optional[str] = None
    cost: Optional[float] = None
    contract_id: Optional[int] = None
    contract_item_id: Optional[int] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CertificateCreate(BaseModel):
    calibration_record_id: int
    file_type: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class CertificateResponse(BaseModel):
    id: int
    calibration_record_id: int
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    uploader: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
