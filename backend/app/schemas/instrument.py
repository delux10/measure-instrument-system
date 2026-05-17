from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class InstrumentCategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


class InstrumentCategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int

    class Config:
        from_attributes = True


class InstrumentCreate(BaseModel):
    code: str
    name: str
    model: Optional[str] = None
    serial_no: Optional[str] = None
    category_id: Optional[int] = None
    range_value: Optional[str] = None
    accuracy: Optional[str] = None
    scale_interval: Optional[str] = None
    manufacture_date: Optional[date] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    keeper: Optional[str] = None
    department_id: Optional[int] = None
    location: Optional[str] = None
    cal_agency: Optional[str] = None
    certificate_no: Optional[str] = None
    cert_confirmed: Optional[str] = None
    metrology_characteristic: Optional[str] = None
    status: str = "in_use"
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    cal_method: Optional[str] = None
    remark: Optional[str] = None


class InstrumentUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    serial_no: Optional[str] = None
    category_id: Optional[int] = None
    range_value: Optional[str] = None
    accuracy: Optional[str] = None
    scale_interval: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    department_id: Optional[int] = None
    keeper: Optional[str] = None
    location: Optional[str] = None
    cal_agency: Optional[str] = None
    certificate_no: Optional[str] = None
    cert_confirmed: Optional[str] = None
    metrology_characteristic: Optional[str] = None
    status: Optional[str] = None
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    cal_method: Optional[str] = None
    remark: Optional[str] = None


class InstrumentResponse(BaseModel):
    id: int
    code: str
    name: str
    model: Optional[str] = None
    serial_no: Optional[str] = None
    category_id: Optional[int] = None
    range_value: Optional[str] = None
    accuracy: Optional[str] = None
    scale_interval: Optional[str] = None
    manufacture_date: Optional[date] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    keeper: Optional[str] = None
    department_id: Optional[int] = None
    location: Optional[str] = None
    cal_agency: Optional[str] = None
    certificate_no: Optional[str] = None
    cert_confirmed: Optional[str] = None
    metrology_characteristic: Optional[str] = None
    status: str
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    cal_method: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImportRowError(BaseModel):
    row: int
    field: Optional[str] = None
    message: str


class ImportResultResponse(BaseModel):
    total_rows: int
    success_count: int
    failure_count: int
    errors: List[ImportRowError] = []
    message: str = ""
