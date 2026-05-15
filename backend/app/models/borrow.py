from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum
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

    instrument = relationship("Instrument")
    from_dept = relationship("Department", foreign_keys=[from_department])
    to_dept = relationship("Department", foreign_keys=[to_department])
