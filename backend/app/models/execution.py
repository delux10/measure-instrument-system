from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
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
