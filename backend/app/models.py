"""统一数据模型 — 全量重构 v2.0"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Department(BaseModel):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    level = Column(Integer, default=1)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    measurer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cost_center = Column(String(50), nullable=True)


class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    role = Column(String(20), default="readonly")
    is_active = Column(Boolean, default=True)
    module_permissions = Column(JSONB, nullable=True)

    department = relationship("Department", foreign_keys=[department_id])


class InstrumentCategory(BaseModel):
    __tablename__ = "instrument_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("instrument_categories.id"), nullable=True)
    level = Column(Integer, default=1)


class Instrument(BaseModel):
    __tablename__ = "instruments"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")

    department = relationship("Department")


class CalibrationAgency(BaseModel):
    __tablename__ = "calibration_agencies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(50), nullable=True)


class CalibrationRecord(BaseModel):
    __tablename__ = "calibration_records"
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    agency_id = Column(Integer, ForeignKey("calibration_agencies.id"), nullable=True)
    plan_date = Column(Date, nullable=True)
    actual_date = Column(Date, nullable=True)
    result = Column(String(50), nullable=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")

    instrument = relationship("Instrument")
    agency = relationship("CalibrationAgency")


class Certificate(BaseModel):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    cert_no = Column(String(100), unique=True, nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    issue_date = Column(Date, nullable=True)
    expire_date = Column(Date, nullable=True)
    file_path = Column(String(500), nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")


class CalibrationContract(BaseModel):
    __tablename__ = "calibration_contracts"
    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("calibration_agencies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    contract_no = Column(String(100), nullable=True)
    total_amount = Column(Float, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")

    agency = relationship("CalibrationAgency")
    items = relationship("ContractItem", back_populates="contract", cascade="all, delete-orphan")


class ContractItem(BaseModel):
    __tablename__ = "contract_items"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("calibration_contracts.id"), nullable=False)
    instrument_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")

    contract = relationship("CalibrationContract", back_populates="items")
    executions = relationship("ExecutionRecord", back_populates="contract_item", cascade="all, delete-orphan")


class ExecutionRecord(BaseModel):
    __tablename__ = "execution_records"
    id = Column(Integer, primary_key=True, index=True)
    contract_item_id = Column(Integer, ForeignKey("contract_items.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    actual_date = Column(Date, nullable=True)
    actual_quantity = Column(Integer, default=1)
    actual_amount = Column(Float, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")

    contract_item = relationship("ContractItem", back_populates="executions")
    instrument = relationship("Instrument")


class ReconciliationDiff(BaseModel):
    __tablename__ = "reconciliation_diffs"
    id = Column(Integer, primary_key=True, index=True)
    contract_item_id = Column(Integer, ForeignKey("contract_items.id"), nullable=True)
    execution_record_id = Column(Integer, ForeignKey("execution_records.id"), nullable=True)
    diff_type = Column(String(50), nullable=False)
    contract_value = Column(String(200), nullable=True)
    actual_value = Column(String(200), nullable=True)
    diff_amount = Column(Float, nullable=True)
    status = Column(String(20), default="open")


class SupervisionExecution(BaseModel):
    __tablename__ = "supervision_executions"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    plan_date = Column(Date, nullable=True)
    executed_date = Column(Date, nullable=True)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="in_progress")
    template_name = Column(String(200), nullable=True)
    check_items = Column(JSONB, default=list, nullable=False, server_default="[]")
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_opinion = Column(Text, nullable=True)
    review_date = Column(Date, nullable=True)

    department = relationship("Department", foreign_keys=[department_id])
    executor = relationship("User", foreign_keys=[executor_id])


class NonConformity(BaseModel):
    __tablename__ = "non_conformities"
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("supervision_executions.id"), nullable=True)
    check_index = Column(Integer, nullable=True)
    ncr_no = Column(String(50), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="general")
    status = Column(String(20), default="issued")
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deadline = Column(Date, nullable=True)
    corrective_action = Column(Text, nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_date = Column(Date, nullable=True)
    fields = Column(JSONB, default=dict, nullable=False, server_default="{}")


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True)
    changes = Column(JSONB, nullable=True)
    summary = Column(String(500), nullable=True)

    user = relationship("User")
    created_at = Column(DateTime, default=func.now(), nullable=False)
