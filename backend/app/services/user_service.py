from app.services.base import BaseCRUDService
from app.models.user import User
from app.utils.auth import get_password_hash
from sqlalchemy.orm import Session
from fastapi import HTTPException


class UserService(BaseCRUDService):
    def __init__(self):
        super().__init__(User, "用户")

    def create(self, db: Session, schema):
        existing = db.query(User).filter(User.username == schema.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        obj = User(
            username=schema.username,
            password_hash=get_password_hash(schema.password),
            name=schema.name,
            phone=schema.phone,
            email=schema.email,
            department_id=schema.department_id,
            role=schema.role,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id: int):
        user = self.get(db, id)
        user.is_active = False
        db.commit()
