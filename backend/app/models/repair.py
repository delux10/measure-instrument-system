from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
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
