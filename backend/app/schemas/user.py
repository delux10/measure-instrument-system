from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: str = "user"
    module_permissions: Optional[List[str]] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    module_permissions: Optional[List[str]] = None


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: str
    is_active: bool
    module_permissions: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
