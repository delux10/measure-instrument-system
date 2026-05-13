from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.supervision import SupervisionPlan
from app.models.user import User
from app.schemas import SupervisionPlanCreate, SupervisionPlanUpdate, SupervisionPlanResponse
from app.utils.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[SupervisionPlanResponse])
def list_plans(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SupervisionPlan)
    if status:
        query = query.filter(SupervisionPlan.status == status)
    if type:
        query = query.filter(SupervisionPlan.type == type)
    if department_id:
        query = query.filter(SupervisionPlan.department_id == department_id)
    return query.all()

@router.get("/{plan_id}", response_model=SupervisionPlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(SupervisionPlan).filter(SupervisionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="监督计划不存在")
    return plan

@router.post("/", response_model=SupervisionPlanResponse)
def create_plan(
    plan: SupervisionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_plan = SupervisionPlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.put("/{plan_id}", response_model=SupervisionPlanResponse)
def update_plan(
    plan_id: int,
    plan: SupervisionPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_plan = db.query(SupervisionPlan).filter(SupervisionPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="监督计划不存在")
    for key, value in plan.model_dump(exclude_unset=True).items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    plan = db.query(SupervisionPlan).filter(SupervisionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="监督计划不存在")
    db.delete(plan)
    db.commit()
    return {"message": "删除成功"}
