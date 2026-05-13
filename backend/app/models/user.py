from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
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
