from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from app.config import settings
from app.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).options(joinedload(User.department)).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def check_role(user: User, required_roles: list) -> bool:
    return user.role in required_roles

def require_role(roles: list):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker

def can_view_all_departments(user: User) -> bool:
    if user.role in ("admin", "system_manager"):
        return True
    if user.department and user.department.name == "工艺质量管理科":
        return True
    return False


def apply_department_filter(query, model, user: User):
    if can_view_all_departments(user):
        return query
    if not user.department_id:
        return query

    if hasattr(model, 'department_id'):
        return query.filter(model.department_id == user.department_id)

    if hasattr(model, 'instrument_id'):
        from app.models.instrument import Instrument as _Instrument
        return query.join(_Instrument).filter(_Instrument.department_id == user.department_id)

    if hasattr(model, 'contract_id'):
        from app.models.contract import CalibrationContract as _CalibrationContract
        return query.join(_CalibrationContract).filter(_CalibrationContract.department_id == user.department_id)

    if hasattr(model, 'calibration_record_id'):
        from app.models.calibration import CalibrationRecord as _CalibrationRecord
        from app.models.instrument import Instrument as _Instrument
        return query.join(_CalibrationRecord).join(_Instrument).filter(_Instrument.department_id == user.department_id)

    # BorrowRecord: from_department or to_department
    from app.models.borrow import BorrowRecord as _BorrowRecord
    if model is _BorrowRecord:
        from sqlalchemy import or_
        return query.filter(or_(
            _BorrowRecord.from_department == user.department_id,
            _BorrowRecord.to_department == user.department_id
        ))

    # SupervisionExecution: target_department_id
    from app.models.supervision import SupervisionExecution as _SupervisionExecution
    if model is _SupervisionExecution:
        return query.filter(_SupervisionExecution.target_department_id == user.department_id)

    return query


def require_module(module_name: str):
    async def module_checker(current_user: User = Depends(get_current_user)):
        perms = current_user.module_permissions
        if perms is None:
            return current_user
        if isinstance(perms, list) and module_name in perms:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该功能模块"
        )
    return module_checker
