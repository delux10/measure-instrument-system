from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# === Auth ===
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[dict] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# === User ===
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: str = "user"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === Department ===
class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    manager_id: Optional[int] = None
    measurer_id: Optional[int] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int
    manager_id: Optional[int] = None
    measurer_id: Optional[int] = None
    children: Optional[List["DepartmentResponse"]] = None
    
    class Config:
        from_attributes = True

# === Instrument Category ===
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

# === Instrument ===
class InstrumentCreate(BaseModel):
    code: str
    name: str
    model: Optional[str] = None
    serial_no: Optional[str] = None
    category_id: Optional[int] = None
    accuracy: Optional[str] = None
    range_value: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacture_date: Optional[date] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    department_id: Optional[int] = None
    keeper: Optional[str] = None
    location: Optional[str] = None
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
    accuracy: Optional[str] = None
    range_value: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    department_id: Optional[int] = None
    keeper: Optional[str] = None
    location: Optional[str] = None
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
    accuracy: Optional[str] = None
    range_value: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacture_date: Optional[date] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    department_id: Optional[int] = None
    keeper: Optional[str] = None
    location: Optional[str] = None
    status: str
    calibration_cycle: Optional[int] = None
    last_cal_date: Optional[date] = None
    next_cal_date: Optional[date] = None
    cal_method: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === Calibration Agency ===
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

# === Calibration Record ===
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

# === Certificate ===
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

# === Calibration Contract ===
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

# === Contract Version ===
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

# === Contract Item ===
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

# === Execution Record ===
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

# === Reconciliation ===
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

# === Supervision Template ===
class SupervisionTemplateCreate(BaseModel):
    name: str
    category: Optional[str] = None
    department_type: Optional[str] = None
    version: str = "1.0"

class SupervisionTemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    department_type: Optional[str] = None
    version: Optional[str] = None

class SupervisionTemplateResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    department_type: Optional[str] = None
    version: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SupervisionTemplateItemCreate(BaseModel):
    template_id: Optional[int] = None
    item_name: str
    standard: Optional[str] = None
    score_standard: Optional[str] = None
    sort_order: int = 0

class SupervisionTemplateItemUpdate(BaseModel):
    item_name: Optional[str] = None
    standard: Optional[str] = None
    score_standard: Optional[str] = None
    sort_order: Optional[int] = None

class SupervisionTemplateItemResponse(BaseModel):
    id: int
    template_id: int
    item_name: str
    standard: Optional[str] = None
    score_standard: Optional[str] = None
    sort_order: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === Supervision Plan ===
class SupervisionPlanCreate(BaseModel):
    type: str
    department_id: Optional[int] = None
    plan_date: Optional[date] = None
    executor_id: Optional[int] = None
    template_id: Optional[int] = None
    remark: Optional[str] = None

class SupervisionPlanUpdate(BaseModel):
    type: Optional[str] = None
    department_id: Optional[int] = None
    plan_date: Optional[date] = None
    executor_id: Optional[int] = None
    template_id: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None

class SupervisionPlanResponse(BaseModel):
    id: int
    type: Optional[str] = None
    department_id: Optional[int] = None
    plan_date: Optional[date] = None
    executor_id: Optional[int] = None
    template_id: Optional[int] = None
    status: str
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === Supervision Execution ===
class SupervisionExecutionCreate(BaseModel):
    plan_id: Optional[int] = None
    template_id: Optional[int] = None
    executor_id: int
    target_department_id: Optional[int] = None
    execution_date: Optional[date] = None
    status: str = "in_progress"

class SupervisionExecutionUpdate(BaseModel):
    template_id: Optional[int] = None
    target_department_id: Optional[int] = None
    execution_date: Optional[date] = None
    status: Optional[str] = None
    overall_result: Optional[str] = None
    reviewer_id: Optional[int] = None
    review_opinion: Optional[str] = None
    review_date: Optional[date] = None

class SupervisionExecutionResponse(BaseModel):
    id: int
    plan_id: Optional[int] = None
    template_id: Optional[int] = None
    executor_id: Optional[int] = None
    target_department_id: Optional[int] = None
    execution_date: Optional[date] = None
    status: str
    overall_result: Optional[str] = None
    reviewer_id: Optional[int] = None
    review_opinion: Optional[str] = None
    review_date: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === Supervision Check Item ===
class SupervisionCheckItemCreate(BaseModel):
    execution_id: Optional[int] = None
    template_item_id: Optional[int] = None
    result: Optional[str] = None
    opinion: Optional[str] = None
    inspector_id: Optional[int] = None

class SupervisionCheckItemUpdate(BaseModel):
    result: Optional[str] = None
    opinion: Optional[str] = None
    evidence_path: Optional[str] = None

class SupervisionCheckItemResponse(BaseModel):
    id: int
    execution_id: int
    template_item_id: Optional[int] = None
    result: Optional[str] = None
    opinion: Optional[str] = None
    evidence_path: Optional[str] = None
    inspector_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === Non-Conformity ===
class NonConformityCreate(BaseModel):
    supervision_execution_id: Optional[int] = None
    check_item_id: Optional[int] = None
    ncr_no: str
    department_id: int
    description: str
    severity: str = "general"
    issued_by: int
    issued_date: Optional[date] = None
    responsible_person: Optional[int] = None
    deadline: Optional[date] = None

class NonConformityUpdate(BaseModel):
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    corrective_action: Optional[str] = None
    corrective_evidence: Optional[str] = None
    responsible_person: Optional[int] = None
    deadline: Optional[date] = None
    verified_by: Optional[int] = None
    verified_date: Optional[date] = None
    verification_result: Optional[str] = None
    remark: Optional[str] = None

class NonConformityResponse(BaseModel):
    id: int
    supervision_execution_id: Optional[int] = None
    check_item_id: Optional[int] = None
    ncr_no: str
    department_id: int
    description: str
    severity: str
    status: str
    issued_by: Optional[int] = None
    issued_date: Optional[date] = None
    corrective_action: Optional[str] = None
    corrective_evidence: Optional[str] = None
    responsible_person: Optional[int] = None
    deadline: Optional[date] = None
    verified_by: Optional[int] = None
    verified_date: Optional[date] = None
    verification_result: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === Workflow ===
class WorkflowCreate(BaseModel):
    type: str
    initiator_id: int
    department_id: Optional[int] = None
    form_data: Optional[str] = None

class WorkflowUpdate(BaseModel):
    status: Optional[str] = None
    form_data: Optional[str] = None
    electronic_sign: Optional[str] = None

class WorkflowResponse(BaseModel):
    id: int
    type: str
    status: str
    initiator_id: Optional[int] = None
    department_id: Optional[int] = None
    form_data: Optional[str] = None
    electronic_sign: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowNodeCreate(BaseModel):
    workflow_id: int
    step_order: int
    approver_id: int

class WorkflowNodeUpdate(BaseModel):
    status: Optional[str] = None
    opinion: Optional[str] = None
    sign_image: Optional[str] = None
    operated_at: Optional[date] = None

class WorkflowNodeResponse(BaseModel):
    id: int
    workflow_id: int
    step_order: Optional[int] = None
    approver_id: Optional[int] = None
    status: str
    opinion: Optional[str] = None
    sign_image: Optional[str] = None
    operated_at: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === Borrow Record ===
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

# === Repair Record ===
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
