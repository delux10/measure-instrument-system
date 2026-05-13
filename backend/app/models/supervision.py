from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class SupervisionType(str, enum.Enum):
    DEPARTMENT = "department"
    CENTRAL = "central"

class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ExecStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"

class CheckResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    NA = "na"

class Severity(str, enum.Enum):
    GENERAL = "general"
    SERIOUS = "serious"

class NcrStatus(str, enum.Enum):
    ISSUED = "issued"
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"

class SupervisionTemplate(BaseModel):
    __tablename__ = "supervision_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(SAEnum(SupervisionType))
    department_type = Column(String(100))
    version = Column(String(20), default="1.0")

class SupervisionTemplateItem(BaseModel):
    __tablename__ = "supervision_template_items"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("supervision_templates.id"), nullable=False)
    item_name = Column(String(500), nullable=False)
    standard = Column(Text)
    score_standard = Column(String(100))
    sort_order = Column(Integer, default=0)

class SupervisionPlan(BaseModel):
    __tablename__ = "supervision_plans"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SAEnum(SupervisionType))
    department_id = Column(Integer, ForeignKey("departments.id"))
    plan_date = Column(Date)
    executor_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("supervision_templates.id"))
    status = Column(SAEnum(PlanStatus), default=PlanStatus.DRAFT)
    remark = Column(Text)

class SupervisionExecution(BaseModel):
    __tablename__ = "supervision_executions"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("supervision_plans.id"))
    template_id = Column(Integer, ForeignKey("supervision_templates.id"))
    executor_id = Column(Integer, ForeignKey("users.id"))
    target_department_id = Column(Integer, ForeignKey("departments.id"))
    execution_date = Column(Date)
    status = Column(SAEnum(ExecStatus), default=ExecStatus.IN_PROGRESS)
    overall_result = Column(String(20))
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_opinion = Column(Text)
    review_date = Column(Date)

class SupervisionCheckItem(BaseModel):
    __tablename__ = "supervision_check_items"
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("supervision_executions.id"), nullable=False)
    template_item_id = Column(Integer, ForeignKey("supervision_template_items.id"))
    result = Column(SAEnum(CheckResult))
    opinion = Column(Text)
    evidence_path = Column(String(500))
    inspector_id = Column(Integer, ForeignKey("users.id"))

class NonConformity(BaseModel):
    __tablename__ = "non_conformities"
    id = Column(Integer, primary_key=True, index=True)
    supervision_execution_id = Column(Integer, ForeignKey("supervision_executions.id"))
    check_item_id = Column(Integer, ForeignKey("supervision_check_items.id"))
    ncr_no = Column(String(50), unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    description = Column(Text, nullable=False)
    severity = Column(SAEnum(Severity))
    status = Column(SAEnum(NcrStatus), default=NcrStatus.ISSUED)
    issued_by = Column(Integer, ForeignKey("users.id"))
    issued_date = Column(Date)
    corrective_action = Column(Text)
    corrective_evidence = Column(String(500))
    responsible_person = Column(Integer, ForeignKey("users.id"))
    deadline = Column(Date)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_date = Column(Date)
    verification_result = Column(String(200))
    remark = Column(Text)
