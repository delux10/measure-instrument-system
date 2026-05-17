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
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    department_id: Optional[int] = None
    status: str = "in_use"
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    extra_data: Optional[dict] = {}


class InstrumentUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[str] = None
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    extra_data: Optional[dict] = None


class InstrumentResponse(BaseModel):
    id: int
    code: str
    name: str
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    status: str
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    extra_data: Optional[dict] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
