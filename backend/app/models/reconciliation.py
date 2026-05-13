from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class DiffType(str, enum.Enum):
    NAME = "name"
    QUANTITY = "quantity"
    PRICE = "price"
    AMOUNT = "amount"
    AGENCY = "agency"
    DEPARTMENT = "department"

class DiffStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ADJUSTED = "adjusted"

class ReconciliationDiff(BaseModel):
    __tablename__ = "reconciliation_diffs"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("calibration_contracts.id"), nullable=False)
    execution_record_id = Column(Integer, ForeignKey("execution_records.id"), nullable=True)
    diff_type = Column(SAEnum(DiffType), nullable=False)
    contract_value = Column(String(200))
    actual_value = Column(String(200))
    diff_value = Column(String(200))
    status = Column(SAEnum(DiffStatus), default=DiffStatus.PENDING)
    remark = Column(Text)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(Date)
    contract = relationship("CalibrationContract")
    execution = relationship("ExecutionRecord")
    confirmer = relationship("User", foreign_keys=[confirmed_by])
