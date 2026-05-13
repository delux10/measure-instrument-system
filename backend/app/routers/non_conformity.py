from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.supervision import NonConformity
from app.models.user import User
from app.schemas import NonConformityCreate, NonConformityUpdate, NonConformityResponse
from app.utils.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[NonConformityResponse])
def list_non_conformities(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    supervision_execution_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(NonConformity)
    if status:
        query = query.filter(NonConformity.status == status)
    if severity:
        query = query.filter(NonConformity.severity == severity)
    if department_id:
        query = query.filter(NonConformity.department_id == department_id)
    if supervision_execution_id:
        query = query.filter(NonConformity.supervision_execution_id == supervision_execution_id)
    return query.all()

@router.get("/{ncr_id}", response_model=NonConformityResponse)
def get_non_conformity(ncr_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ncr = db.query(NonConformity).filter(NonConformity.id == ncr_id).first()
    if not ncr:
        raise HTTPException(status_code=404, detail="不符合项不存在")
    return ncr

@router.post("/", response_model=NonConformityResponse)
def create_non_conformity(
    ncr: NonConformityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    from datetime import date
    existing = db.query(NonConformity).filter(NonConformity.ncr_no == ncr.ncr_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="不符合项编号已存在")
    db_ncr = NonConformity(**ncr.model_dump(exclude={"issued_date"}))
    db_ncr.issued_date = ncr.issued_date or date.today()
    db.add(db_ncr)
    db.commit()
    db.refresh(db_ncr)
    return db_ncr

@router.put("/{ncr_id}", response_model=NonConformityResponse)
def update_non_conformity(
    ncr_id: int,
    ncr: NonConformityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_ncr = db.query(NonConformity).filter(NonConformity.id == ncr_id).first()
    if not db_ncr:
        raise HTTPException(status_code=404, detail="不符合项不存在")
    for key, value in ncr.model_dump(exclude_unset=True).items():
        setattr(db_ncr, key, value)
    db.commit()
    db.refresh(db_ncr)
    return db_ncr

@router.delete("/{ncr_id}")
def delete_non_conformity(
    ncr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    ncr = db.query(NonConformity).filter(NonConformity.id == ncr_id).first()
    if not ncr:
        raise HTTPException(status_code=404, detail="不符合项不存在")
    db.delete(ncr)
    db.commit()
    return {"message": "删除成功"}
