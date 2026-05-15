from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


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
