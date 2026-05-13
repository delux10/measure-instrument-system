from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class WorkflowType(str, enum.Enum):
    PURCHASE = "purchase"
    SCRAP = "scrap"
    TRANSFER = "transfer"

class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class NodeStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Workflow(BaseModel):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SAEnum(WorkflowType), nullable=False)
    status = Column(SAEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    initiator_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    form_data = Column(Text)
    electronic_sign = Column(String(500))

class WorkflowNode(BaseModel):
    __tablename__ = "workflow_nodes"
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    step_order = Column(Integer)
    approver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SAEnum(NodeStatus), default=NodeStatus.PENDING)
    opinion = Column(Text)
    sign_image = Column(String(500))
    operated_at = Column(Date)
