from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.execution import ExecutionRecord
from app.models.user import User
from app.schemas import ExecutionRecordCreate, ExecutionRecordUpdate, ExecutionRecordResponse
from app.utils.auth import get_current_user, require_role, apply_department_filter

router = APIRouter()

@router.get("/", response_model=List[ExecutionRecordResponse])
def list_records(
    contract_id: Optional[int] = Query(None),
    instrument_id: Optional[int] = Query(None),
    agency_id: Optional[int] = Query(None),
    payment_status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ExecutionRecord)
    if contract_id:
        query = query.join(ExecutionRecord.contract_item).filter(
            ExecutionRecord.contract_item.has(contract_id=contract_id)
        )
    if instrument_id:
        query = query.filter(ExecutionRecord.instrument_id == instrument_id)
    if agency_id:
        query = query.filter(ExecutionRecord.agency_id == agency_id)
    if payment_status:
        query = query.filter(ExecutionRecord.payment_status == payment_status)
    if start_date:
        query = query.filter(ExecutionRecord.actual_date >= start_date)
    if end_date:
        query = query.filter(ExecutionRecord.actual_date <= end_date)
    query = apply_department_filter(query, ExecutionRecord, current_user)
    return query.all()

@router.get("/{record_id}", response_model=ExecutionRecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(ExecutionRecord).filter(ExecutionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return record

@router.post("/", response_model=ExecutionRecordResponse)
def create_record(
    record: ExecutionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_record = ExecutionRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/{record_id}", response_model=ExecutionRecordResponse)
def update_record(
    record_id: int,
    record: ExecutionRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_record = db.query(ExecutionRecord).filter(ExecutionRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    for key, value in record.model_dump(exclude_unset=True).items():
        setattr(db_record, key, value)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    record = db.query(ExecutionRecord).filter(ExecutionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
