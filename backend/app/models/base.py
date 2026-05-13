from datetime import datetime
from sqlalchemy import Column, DateTime, func
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
