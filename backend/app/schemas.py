"""Pydantic schemas — 统一 API 响应格式"""
from typing import Optional, List, Any
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str; password: str

class UserCreate(BaseModel):
    username: str; password: str; name: str
    role: str = "dept_measurer"; department_id: Optional[int] = None
    phone: Optional[str] = None; email: Optional[str] = None
    module_permissions: Optional[List[str]] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None; role: Optional[str] = None
    department_id: Optional[int] = None; phone: Optional[str] = None
    email: Optional[str] = None; is_active: Optional[bool] = None
    module_permissions: Optional[List[str]] = None

class DepartmentCreate(BaseModel):
    name: str; parent_id: Optional[int] = None; level: int = 1

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None; parent_id: Optional[int] = None
    manager_id: Optional[int] = None; measurer_id: Optional[int] = None
    cost_center: Optional[str] = None

class InstrumentCreate(BaseModel):
    department_id: Optional[int] = None; fields: dict = {}

class InstrumentUpdate(BaseModel):
    department_id: Optional[int] = None; fields: Optional[dict] = None

class CalibrationAgencyCreate(BaseModel):
    name: str; address: Optional[str] = None
    contact_person: Optional[str] = None; contact_phone: Optional[str] = None

class CalibrationRecordCreate(BaseModel):
    instrument_id: int; agency_id: Optional[int] = None
    plan_date: Optional[str] = None; actual_date: Optional[str] = None
    result: Optional[str] = None; department_id: Optional[int] = None; fields: dict = {}

class CalibrationRecordUpdate(BaseModel):
    agency_id: Optional[int] = None; plan_date: Optional[str] = None
    actual_date: Optional[str] = None; result: Optional[str] = None
    fields: Optional[dict] = None

class ContractCreate(BaseModel):
    agency_id: int; year: int; contract_no: Optional[str] = None
    total_amount: Optional[float] = None; department_id: Optional[int] = None; fields: dict = {}

class ContractItemCreate(BaseModel):
    instrument_name: str; quantity: int = 1
    unit_price: Optional[float] = None; amount: Optional[float] = None
    department_id: Optional[int] = None; fields: dict = {}

class ExecutionRecordCreate(BaseModel):
    contract_item_id: int; instrument_id: Optional[int] = None
    actual_date: Optional[str] = None; actual_quantity: int = 1
    actual_amount: Optional[float] = None; department_id: Optional[int] = None; fields: dict = {}

class ImportResult(BaseModel):
    total_rows: int = 0; success_count: int = 0; failure_count: int = 0
    errors: List[dict] = []; message: str = ""

class SupervisionCreate(BaseModel):
    department_id: int; plan_date: Optional[str] = None
    executor_id: Optional[int] = None; template_name: Optional[str] = None
    check_items: List[dict] = []

class SupervisionUpdate(BaseModel):
    executed_date: Optional[str] = None; status: Optional[str] = None
    check_items: Optional[List[dict]] = None

class SupervisionReview(BaseModel):
    opinion: str; action: str

class NcrCreate(BaseModel):
    execution_id: Optional[int] = None; check_index: Optional[int] = None
    ncr_no: str; department_id: Optional[int] = None; description: str
    severity: str = "general"; issued_by: Optional[int] = None
    deadline: Optional[str] = None; fields: dict = {}

class NcrUpdate(BaseModel):
    status: Optional[str] = None; corrective_action: Optional[str] = None
    verified_by: Optional[int] = None; fields: Optional[dict] = None
