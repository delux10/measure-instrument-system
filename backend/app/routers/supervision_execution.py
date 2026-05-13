from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.supervision import SupervisionExecution, SupervisionCheckItem
from app.models.user import User
from app.schemas import (
    SupervisionExecutionCreate, SupervisionExecutionUpdate, SupervisionExecutionResponse,
    SupervisionCheckItemCreate, SupervisionCheckItemUpdate, SupervisionCheckItemResponse
)
from app.utils.auth import get_current_user, require_role

router = APIRouter()

# === Execution CRUD ===

@router.get("/", response_model=List[SupervisionExecutionResponse])
def list_executions(
    plan_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    executor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SupervisionExecution)
    if plan_id:
        query = query.filter(SupervisionExecution.plan_id == plan_id)
    if status:
        query = query.filter(SupervisionExecution.status == status)
    if executor_id:
        query = query.filter(SupervisionExecution.executor_id == executor_id)
    return query.all()

@router.get("/{exec_id}", response_model=SupervisionExecutionResponse)
def get_execution(exec_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exec_ = db.query(SupervisionExecution).filter(SupervisionExecution.id == exec_id).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="监督执行记录不存在")
    return exec_

@router.post("/", response_model=SupervisionExecutionResponse)
def create_execution(
    exec_: SupervisionExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_exec = SupervisionExecution(**exec_.model_dump())
    db.add(db_exec)
    db.commit()
    db.refresh(db_exec)
    return db_exec

@router.put("/{exec_id}", response_model=SupervisionExecutionResponse)
def update_execution(
    exec_id: int,
    exec_: SupervisionExecutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_exec = db.query(SupervisionExecution).filter(SupervisionExecution.id == exec_id).first()
    if not db_exec:
        raise HTTPException(status_code=404, detail="监督执行记录不存在")
    for key, value in exec_.model_dump(exclude_unset=True).items():
        setattr(db_exec, key, value)
    db.commit()
    db.refresh(db_exec)
    return db_exec

@router.delete("/{exec_id}")
def delete_execution(
    exec_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    exec_ = db.query(SupervisionExecution).filter(SupervisionExecution.id == exec_id).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="监督执行记录不存在")
    db.query(SupervisionCheckItem).filter(SupervisionCheckItem.execution_id == exec_id).delete()
    db.delete(exec_)
    db.commit()
    return {"message": "删除成功"}

# === Review ===

@router.post("/{exec_id}/review")
def review_execution(
    exec_id: int,
    review: SupervisionExecutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    from datetime import date
    db_exec = db.query(SupervisionExecution).filter(SupervisionExecution.id == exec_id).first()
    if not db_exec:
        raise HTTPException(status_code=404, detail="监督执行记录不存在")
    db_exec.reviewer_id = current_user.id
    db_exec.review_date = date.today()
    if review.overall_result is not None:
        db_exec.overall_result = review.overall_result
    if review.review_opinion is not None:
        db_exec.review_opinion = review.review_opinion
    if review.status is not None:
        db_exec.status = review.status
    db.commit()
    db.refresh(db_exec)
    return db_exec

# === Check Items ===

@router.get("/{exec_id}/check-items", response_model=List[SupervisionCheckItemResponse])
def list_check_items(exec_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SupervisionCheckItem).filter(SupervisionCheckItem.execution_id == exec_id).all()

@router.post("/{exec_id}/check-items", response_model=SupervisionCheckItemResponse)
def create_check_item(
    exec_id: int,
    item: SupervisionCheckItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exec_ = db.query(SupervisionExecution).filter(SupervisionExecution.id == exec_id).first()
    if not exec_:
        raise HTTPException(status_code=404, detail="监督执行记录不存在")
    db_item = SupervisionCheckItem(execution_id=exec_id, **item.model_dump(exclude={"execution_id"}))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{exec_id}/check-items/{item_id}", response_model=SupervisionCheckItemResponse)
def update_check_item(
    exec_id: int,
    item_id: int,
    item: SupervisionCheckItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(SupervisionCheckItem).filter(
        SupervisionCheckItem.id == item_id,
        SupervisionCheckItem.execution_id == exec_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="检查项目不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{exec_id}/check-items/{item_id}")
def delete_check_item(
    exec_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    db_item = db.query(SupervisionCheckItem).filter(
        SupervisionCheckItem.id == item_id,
        SupervisionCheckItem.execution_id == exec_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="检查项目不存在")
    db.delete(db_item)
    db.commit()
    return {"message": "删除成功"}
