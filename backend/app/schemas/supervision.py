from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


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
