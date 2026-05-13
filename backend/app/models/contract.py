from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum, Text
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
