"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest
from app.utils.auth import verify_password, create_token, get_current_user, hash_password

router = APIRouter()

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(403, detail="账号已停用")
    token = create_token({
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "module_permissions": user.module_permissions,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id, "username": user.username, "name": user.name,
            "role": user.role, "department_id": user.department_id,
            "module_permissions": user.module_permissions,
        }
    }

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"data": {
        "id": user.id, "username": user.username, "name": user.name,
        "role": user.role, "department_id": user.department_id,
        "department_name": user.department.name if user.department else None,
        "module_permissions": user.module_permissions,
    }}

@router.post("/logout")
def logout():
    return {"data": None, "meta": None}
