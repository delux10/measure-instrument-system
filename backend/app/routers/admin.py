"""系统管理路由 — 用户、部门、分类"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User, Department, InstrumentCategory, AuditLog
from app.schemas import UserCreate, UserUpdate, DepartmentCreate, DepartmentUpdate
from app.utils.auth import get_current_user, require_role, hash_password
from app.utils.audit import log

router = APIRouter()

# ── 用户列表 ──
@router.get("/users")
def list_users(search: str = Query(None), db: Session = Depends(get_db),
               current_user: User = Depends(require_role(["admin", "system_manager"]))):
    query = db.query(User)
    if search: query = query.filter(User.username.ilike(f"%{search}%") | User.name.ilike(f"%{search}%"))
    items = query.order_by(User.id).all()
    return {"data": [{"id": u.id, "username": u.username, "name": u.name, "role": u.role,
                      "department_id": u.department_id, "phone": u.phone, "email": u.email,
                      "is_active": u.is_active, "module_permissions": u.module_permissions,
                      "created_at": str(u.created_at) if u.created_at else None} for u in items], "meta": None}

# ── 创建用户 ──
@router.post("/users")
def create_user(body: UserCreate, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(["admin"]))):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(400, detail="用户名已存在")
    user = User(username=body.username, password_hash=hash_password(body.password),
                name=body.name, role=body.role, department_id=body.department_id,
                phone=body.phone, email=body.email, module_permissions=body.module_permissions)
    db.add(user); db.flush()
    log(db, current_user.id, "create", "user", user.id, summary=f"创建用户 {user.username}")
    db.commit(); db.refresh(user)
    return {"data": {"id": user.id, "username": user.username}}

# ── 更新用户 ──
@router.put("/users/{user_id}")
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(["admin", "system_manager"]))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, detail="用户不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None: setattr(user, k, v)
    log(db, current_user.id, "update", "user", user_id, summary=f"更新用户 {user.username}")
    db.commit()
    return {"data": {"id": user.id}}

# ── 删除用户 ──
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(["admin"]))):
    if user_id == current_user.id: raise HTTPException(400, detail="不能删除自己")
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, detail="用户不存在")
    log(db, current_user.id, "delete", "user", user_id, summary=f"删除用户 {user.username}")
    db.delete(user); db.commit()
    return {"data": None}

# ── 部门列表（含台账「所属部门」自动同步）─
@router.get("/departments")
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 从台账 fields JSONB 提取所有唯一的「所属部门」，自动创建缺失的部门
    rows = db.execute(text(
        "SELECT DISTINCT fields->>'所属部门' AS name FROM instruments "
        "WHERE fields ? '所属部门' AND fields->>'所属部门' IS NOT NULL AND trim(fields->>'所属部门') != ''"
    )).fetchall()
    for (name,) in rows:
        name = name.strip()
        if not db.query(Department).filter(Department.name == name).first():
            db.add(Department(name=name, level=1))
    db.commit()
    depts = db.query(Department).order_by(Department.level, Department.id).all()
    return {"data": [{"id": d.id, "name": d.name, "parent_id": d.parent_id, "level": d.level,
                      "manager_id": d.manager_id, "measurer_id": d.measurer_id, "cost_center": d.cost_center}
                     for d in depts], "meta": None}

# ── 创建部门 ──
@router.post("/departments")
def create_department(body: DepartmentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(require_role(["admin"]))):
    d = Department(**body.model_dump())
    db.add(d); db.commit(); db.refresh(d)
    return {"data": {"id": d.id, "name": d.name}}

# ── 更新部门 ──
@router.put("/departments/{dept_id}")
def update_department(dept_id: int, body: DepartmentUpdate, db: Session = Depends(get_db),
                      current_user: User = Depends(require_role(["admin"]))):
    d = db.query(Department).filter(Department.id == dept_id).first()
    if not d: raise HTTPException(404, detail="部门不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None: setattr(d, k, v)
    db.commit()
    return {"data": {"id": d.id}}

# ── 分类列表 ──
@router.get("/categories")
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cats = db.query(InstrumentCategory).order_by(InstrumentCategory.level, InstrumentCategory.id).all()
    return {"data": [{"id": c.id, "name": c.name, "parent_id": c.parent_id, "level": c.level} for c in cats], "meta": None}

# ── 创建分类 ──
@router.post("/categories")
def create_category(name: str = Query(...), parent_id: int = Query(None), db: Session = Depends(get_db),
                    current_user: User = Depends(require_role(["admin"]))):
    level = 1
    if parent_id:
        parent = db.query(InstrumentCategory).filter(InstrumentCategory.id == parent_id).first()
        if parent: level = parent.level + 1
    c = InstrumentCategory(name=name, parent_id=parent_id, level=level)
    db.add(c); db.commit(); db.refresh(c)
    return {"data": {"id": c.id, "name": c.name}}

# ── 审计日志 ──
@router.get("/audit-logs")
def list_audit_logs(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100),
                    target_type: str = Query(None), user_id: int = Query(None),
                    db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    query = db.query(AuditLog)
    if target_type: query = query.filter(AuditLog.target_type == target_type)
    if user_id: query = query.filter(AuditLog.user_id == user_id)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": [{"id": a.id, "user_id": a.user_id, "action": a.action, "target_type": a.target_type,
                      "target_id": a.target_id, "changes": a.changes, "summary": a.summary,
                      "user_name": a.user.name if a.user else None,
                      "created_at": str(a.created_at)} for a in items],
            "meta": {"total": total, "page": page, "page_size": page_size}}
