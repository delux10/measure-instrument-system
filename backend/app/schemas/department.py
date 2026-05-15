from pydantic import BaseModel
from typing import Optional, List


class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    manager_id: Optional[int] = None
    measurer_id: Optional[int] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int
    manager_id: Optional[int] = None
    measurer_id: Optional[int] = None
    children: Optional[List["DepartmentResponse"]] = None

    class Config:
        from_attributes = True
