from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: str = "user"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
