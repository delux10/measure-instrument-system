from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
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
