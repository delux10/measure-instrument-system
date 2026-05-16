from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
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
    range_value = Column(String(100))
    accuracy = Column(String(100))
    scale_interval = Column(String(50))
    manufacture_date = Column(Date)
    manufacturer = Column(String(200))
    purchase_date = Column(Date)
    price = Column(Float)
    keeper = Column(String(50))
    department_id = Column(Integer, ForeignKey("departments.id"))
    location = Column(String(200))
    cal_agency = Column(String(200))
    certificate_no = Column(String(100))
    cert_confirmed = Column(String(50))
    metrology_characteristic = Column(String(200))
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
