import os

base = "/Users/hujiong/projects/measure-instrument-system/backend/app"

files = {}

# Base model
files["models/base.py"] = """from datetime import datetime
from sqlalchemy import Column, DateTime, func
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
"""

# Department model
files["models/department.py"] = """from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Department(BaseModel):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    level = Column(Integer, default=1)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    measurer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    children = relationship("Department", backref="parent", remote_side=[id])
"""

# User
files["models/user.py"] = """from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    department = relationship("Department", foreign_keys=[department_id])
"""

# Instrument
files["models/instrument.py"] = """from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class InstrumentStatus(str, enum.Enum):
    IN_USE = "in_use"
    IDLE = "idle"
    REPAIR = "repair"
    SCRAPPED = "scrapped"
    CALIBRATING = "calibrating"
    STOPPED = "stopped"

class InstrumentCategory(BaseModel):
    __tablename__ = "instrument_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("instrument_categories.id"), nullable=True)
    level = Column(Integer, default=1)
    children = relationship("InstrumentCategory", backref="parent", remote_side=[id])

class Instrument(BaseModel):
    __tablename__ = "instruments"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    model = Column(String(200))
    serial_no = Column(String(200))
    category_id = Column(Integer, ForeignKey("instrument_categories.id"))
    accuracy = Column(String(100))
    range_value = Column(String(100))
    manufacturer = Column(String(200))
    manufacture_date = Column(Date)
    purchase_date = Column(Date)
    price = Column(Float)
    department_id = Column(Integer, ForeignKey("departments.id"))
    keeper = Column(String(50))
    location = Column(String(200))
    status = Column(SAEnum(InstrumentStatus), default=InstrumentStatus.IN_USE)
    photo = Column(String(500))
    calibration_cycle = Column(Integer)
    last_cal_date = Column(Date)
    next_cal_date = Column(Date)
    cal_method = Column(String(50))
    last_cal_cost = Column(Float)
    remark = Column(String(500))
    category = relationship("InstrumentCategory")
    department = relationship("Department")
"""

# Calibration
files["models/calibration.py"] = """from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CalResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    ADJUST = "adjust"

class CalibrationAgency(BaseModel):
    __tablename__ = "calibration_agencies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    qualification = Column(String(500))
    contact = Column(String(100))
    phone = Column(String(50))
    address = Column(String(200))
    service_range = Column(String(500))
    cooperation_end = Column(Date)
    remark = Column(String(500))

class CalibrationRecord(BaseModel):
    __tablename__ = "calibration_records"
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    plan_date = Column(Date)
    actual_date = Column(Date)
    agency_id = Column(Integer, ForeignKey("calibration_agencies.id"))
    result = Column(SAEnum(CalResult))
    certificate_no = Column(String(100))
    cost = Column(Float)
    contract_id = Column(Integer, ForeignKey("calibration_contracts.id"), nullable=True)
    contract_item_id = Column(Integer, ForeignKey("contract_items.id"), nullable=True)
    operator = Column(String(50))
    remark = Column(String(500))
    instrument = relationship("Instrument")
    agency = relationship("CalibrationAgency")

class Certificate(BaseModel):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    calibration_record_id = Column(Integer, ForeignKey("calibration_records.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20))
    valid_from = Column(Date)
    valid_until = Column(Date)
    uploader = Column(String(50))
    calibration_record = relationship("CalibrationRecord")
"""

# Contract
files["models/contract.py"] = """from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class ContractStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CalibrationContract(BaseModel):
    __tablename__ = "calibration_contracts"
    id = Column(Integer, primary_key=True, index=True)
    contract_no = Column(String(50), unique=True, nullable=False)
    name = Column(String(200))
    agency_id = Column(Integer, ForeignKey("calibration_agencies.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    contract_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    total_amount = Column(Float)
    payment_terms = Column(String(500))
    invoice_title = Column(String(200))
    tax_id = Column(String(50))
    invoice_type = Column(String(20))
    tax_rate = Column(Float)
    status = Column(SAEnum(ContractStatus), default=ContractStatus.PENDING)
    remark = Column(Text)
    agency = relationship("CalibrationAgency")
    department = relationship("Department")
    versions = relationship("ContractVersion", back_populates="contract")

class ContractVersion(BaseModel):
    __tablename__ = "contract_versions"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("calibration_contracts.id"), nullable=False)
    version_no = Column(String(20), nullable=False)
    version_label = Column(String(200))
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(100))
    uploader_id = Column(Integer, ForeignKey("users.id"))
    is_current = Column(Integer, default=0)
    remark = Column(String(500))
    contract = relationship("CalibrationContract", back_populates="versions")
    uploader = relationship("User")

class ContractItem(BaseModel):
    __tablename__ = "contract_items"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("calibration_contracts.id"), nullable=False)
    instrument_name = Column(String(200), nullable=False)
    specification = Column(String(200))
    quantity = Column(Integer)
    unit_price = Column(Float)
    amount = Column(Float)
    remark = Column(String(500))
    contract = relationship("CalibrationContract")
"""

# Execution
files["models/execution.py"] = """from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"

class ExecutionRecord(BaseModel):
    __tablename__ = "execution_records"
    id = Column(Integer, primary_key=True, index=True)
    contract_item_id = Column(Integer, ForeignKey("contract_items.id"), nullable=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    agency_id = Column(Integer, ForeignKey("calibration_agencies.id"))
    actual_date = Column(Date)
    actual_quantity = Column(Integer)
    actual_unit_price = Column(Float)
    actual_amount = Column(Float)
    result = Column(String(20))
    certificate_no = Column(String(100))
    invoice_no = Column(String(100))
    invoice_date = Column(Date)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.UNPAID)
    payment_amount = Column(Float, default=0)
    payment_date = Column(Date)
    contract_item = relationship("ContractItem")
    instrument = relationship("Instrument")
    department = relationship("Department")
    agency = relationship("CalibrationAgency")
"""

# Reconciliation
files["models/reconciliation.py"] = """from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SAEnum, Text
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
"""

# Supervision
files["models/supervision.py"] = """from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum, Text
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
"""

# Workflow
files["models/workflow.py"] = """from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Text
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
"""

# Borrow
files["models/borrow.py"] = """from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class BorrowStatus(str, enum.Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"

class BorrowRecord(BaseModel):
    __tablename__ = "borrow_records"
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    from_department = Column(Integer, ForeignKey("departments.id"))
    to_department = Column(Integer, ForeignKey("departments.id"))
    borrower = Column(String(50))
    expected_return_date = Column(Date)
    actual_return_date = Column(Date)
    status = Column(SAEnum(BorrowStatus), default=BorrowStatus.BORROWED)
"""

# Repair
files["models/repair.py"] = """from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairRecord(BaseModel):
    __tablename__ = "repair_records"
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    fault_description = Column(Text)
    repair_content = Column(Text)
    cost = Column(Float)
    repair_party = Column(String(200))
    repair_date = Column(Date)
    operator = Column(String(50))
    remark = Column(Text)
"""

# __init__.py
files["models/__init__.py"] = """from app.models.base import BaseModel
from app.models.department import Department
from app.models.user import User
from app.models.instrument import Instrument, InstrumentCategory, InstrumentStatus
from app.models.calibration import CalibrationRecord, Certificate, CalibrationAgency, CalResult
from app.models.contract import CalibrationContract, ContractVersion, ContractItem, ContractStatus
from app.models.execution import ExecutionRecord, PaymentStatus
from app.models.reconciliation import ReconciliationDiff, DiffType, DiffStatus
from app.models.supervision import (
    SupervisionTemplate, SupervisionTemplateItem,
    SupervisionPlan, SupervisionExecution,
    SupervisionCheckItem, NonConformity,
    SupervisionType, PlanStatus, ExecStatus, CheckResult, Severity, NcrStatus
)
from app.models.workflow import Workflow, WorkflowNode, WorkflowType, WorkflowStatus, NodeStatus
from app.models.borrow import BorrowRecord, BorrowStatus
from app.models.repair import RepairRecord
"""

# Write all files
for rel_path, content in files.items():
    full_path = os.path.join(base, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"OK: {rel_path}")

print("\nAll model files created successfully!")
