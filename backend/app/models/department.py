from sqlalchemy import Column, Integer, String, ForeignKey
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
