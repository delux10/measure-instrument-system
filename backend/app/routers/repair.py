from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.repair import RepairRecord
from app.models.user import User
from app.schemas import RepairCreate, RepairUpdate, RepairResponse
from app.utils.auth import get_current_user, require_role, apply_department_filter

router = APIRouter()

@router.get("/", response_model=List[RepairResponse])
def list_repairs(
    instrument_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(RepairRecord)
    if instrument_id:
        query = query.filter(RepairRecord.instrument_id == instrument_id)
    query = apply_department_filter(query, RepairRecord, current_user)
    return query.order_by(RepairRecord.repair_date.desc().nullslast()).all()

@router.get("/{repair_id}", response_model=RepairResponse)
def get_repair(repair_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(RepairRecord).filter(RepairRecord.id == repair_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="维修记录不存在")
    return record

@router.post("/", response_model=RepairResponse)
def create_repair(
    repair: RepairCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_record = RepairRecord(**repair.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/{repair_id}", response_model=RepairResponse)
def update_repair(
    repair_id: int,
    repair: RepairUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_record = db.query(RepairRecord).filter(RepairRecord.id == repair_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="维修记录不存在")
    for key, value in repair.model_dump(exclude_unset=True).items():
        setattr(db_record, key, value)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{repair_id}")
def delete_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    record = db.query(RepairRecord).filter(RepairRecord.id == repair_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="维修记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
