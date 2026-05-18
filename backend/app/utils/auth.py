"""
认证与权限工具 — 独立实现
"""
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload
from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效凭据")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        uid: int = payload.get("user_id")
        if uid is None:
            raise exc
    except JWTError:
        raise exc
    user = db.query(User).options(joinedload(User.department)).filter(User.id == uid).first()
    if not user or not user.is_active:
        raise exc
    return user

def require_role(roles: list):
    async def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="权限不足")
        return user
    return checker

def can_view_all(user: User) -> bool:
    if user.role in ("admin", "system_manager"):
        return True
    if user.department and user.department.name == "工艺质量管理科":
        return True
    return False

def apply_department_filter(query, model, user: User):
    if can_view_all(user):
        return query
    if user.department_id and hasattr(model, "department_id"):
        return query.filter(model.department_id == user.department_id)
    return query

def require_module(name: str):
    async def checker(user: User = Depends(get_current_user)):
        perms = user.module_permissions
        if perms is None:
            return user
        if isinstance(perms, list) and name in perms:
            return user
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="无权访问该模块")
    return checker
