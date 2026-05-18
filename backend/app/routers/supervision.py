"""监督管理路由 — 简化为 执行登记 + 不符合项"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import SupervisionExecution, NonConformity, User
from app.schemas import SupervisionCreate, SupervisionUpdate, SupervisionReview, NcrCreate, NcrUpdate
from app.utils.auth import get_current_user, require_role, apply_department_filter

router = APIRouter()

# ── 执行记录列表 ──
@router.get("/executions")
def list_executions(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                    status: str = Query(None), db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    query = apply_department_filter(db.query(SupervisionExecution), SupervisionExecution, current_user)
    if status: query = query.filter(SupervisionExecution.status == status)
    total = query.count()
    items = query.order_by(SupervisionExecution.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": [_fmt_exec(e) for e in items], "meta": {"total": total, "page": page, "page_size": page_size}}

# ── 创建执行 ──
@router.post("/executions")
def create_execution(body: SupervisionCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_role(["admin", "system_manager", "dept_measurer"]))):
    exec_rec = SupervisionExecution(department_id=body.department_id, plan_date=body.plan_date,
                                    executor_id=body.executor_id or current_user.id,
                                    template_name=body.template_name, check_items=body.check_items)
    db.add(exec_rec); db.commit(); db.refresh(exec_rec)
    return {"data": _fmt_exec(exec_rec)}

# ── 更新执行（填写检查结果、提交完成） ──
@router.put("/executions/{execution_id}")
def update_execution(execution_id: int, body: SupervisionUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_role(["admin", "system_manager", "dept_measurer"]))):
    exec_rec = db.query(SupervisionExecution).filter(SupervisionExecution.id == execution_id).first()
    if not exec_rec: raise HTTPException(404, detail="执行记录不存在")
    if body.executed_date: exec_rec.executed_date = body.executed_date
    if body.status: exec_rec.status = body.status
    if body.check_items is not None: exec_rec.check_items = body.check_items
    # 自动生成不符合项
    if body.check_items:
        for idx, item in enumerate(body.check_items):
            if item.get("result") == "fail":
                existing = db.query(NonConformity).filter(
                    NonConformity.execution_id == execution_id, NonConformity.check_index == idx).first()
                if not existing:
                    ncr_no = f"NCR-{date.today().strftime('%Y%m%d')}-{idx+1:03d}"
                    # ensure unique
                    while db.query(NonConformity).filter(NonConformity.ncr_no == ncr_no).first():
                        import uuid
                        ncr_no = f"NCR-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                    ncr = NonConformity(execution_id=execution_id, check_index=idx, ncr_no=ncr_no,
                                        department_id=exec_rec.department_id, description=item.get("item_name", ""),
                                        severity="general")
                    db.add(ncr)
    db.commit(); db.refresh(exec_rec)
    return {"data": _fmt_exec(exec_rec)}

# ── 审核 ──
@router.post("/executions/{execution_id}/review")
def review_execution(execution_id: int, body: SupervisionReview, db: Session = Depends(get_db),
                     current_user: User = Depends(require_role(["admin", "system_manager"]))):
    exec_rec = db.query(SupervisionExecution).filter(SupervisionExecution.id == execution_id).first()
    if not exec_rec: raise HTTPException(404, detail="执行记录不存在")
    exec_rec.status = body.action  # approved / rejected
    exec_rec.reviewer_id = current_user.id
    exec_rec.review_opinion = body.opinion
    exec_rec.review_date = date.today()
    db.commit()
    return {"data": _fmt_exec(exec_rec)}

# ── NCR 列表 ──
@router.get("/non-conformities")
def list_ncrs(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
              status: str = Query(None), severity: str = Query(None), db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    query = apply_department_filter(db.query(NonConformity), NonConformity, current_user)
    if status: query = query.filter(NonConformity.status == status)
    if severity: query = query.filter(NonConformity.severity == severity)
    total = query.count()
    items = query.order_by(NonConformity.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": [{"id": n.id, "execution_id": n.execution_id, "check_index": n.check_index,
                      "ncr_no": n.ncr_no, "department_id": n.department_id, "description": n.description,
                      "severity": n.severity, "status": n.status, "deadline": str(n.deadline) if n.deadline else None,
                      "corrective_action": n.corrective_action,
                      "verified_date": str(n.verified_date) if n.verified_date else None,
                      "created_at": str(n.created_at) if n.created_at else None} for n in items],
            "meta": {"total": total, "page": page, "page_size": page_size}}

# ── 创建 NCR ──
@router.post("/non-conformities")
def create_ncr(body: NcrCreate, db: Session = Depends(get_db),
               current_user: User = Depends(require_role(["admin", "system_manager"]))):
    ncr = NonConformity(**{k: v for k, v in body.model_dump().items() if v is not None})
    db.add(ncr); db.commit(); db.refresh(ncr)
    return {"data": {"id": ncr.id, "ncr_no": ncr.ncr_no}}

# ── 更新 NCR (状态流转) ──
@router.put("/non-conformities/{ncr_id}")
def update_ncr(ncr_id: int, body: NcrUpdate, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    ncr = db.query(NonConformity).filter(NonConformity.id == ncr_id).first()
    if not ncr: raise HTTPException(404, detail="不符合项不存在")
    if body.status: ncr.status = body.status
    if body.corrective_action: ncr.corrective_action = body.corrective_action
    if body.verified_by: ncr.verified_by = body.verified_by
    if body.status == "verified" and not ncr.verified_date:
        ncr.verified_date = date.today()
    if body.fields: ncr.fields = {**(ncr.fields or {}), **body.fields}
    db.commit()
    return {"data": {"id": ncr.id, "status": ncr.status}}

def _fmt_exec(e):
    return {"id": e.id, "department_id": e.department_id, "plan_date": str(e.plan_date) if e.plan_date else None,
            "executed_date": str(e.executed_date) if e.executed_date else None,
            "executor_id": e.executor_id, "status": e.status, "template_name": e.template_name,
            "check_items": e.check_items or [], "review_opinion": e.review_opinion,
            "review_date": str(e.review_date) if e.review_date else None,
            "department_name": e.department.name if e.department else None,
            "created_at": str(e.created_at) if e.created_at else None}
