from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.calibration import CalibrationRecord
from app.models.user import User
from app.schemas import CalibrationRecordCreate, CalibrationRecordUpdate, CalibrationRecordResponse
from app.utils.auth import get_current_user, require_role, apply_department_filter

router = APIRouter()

@router.get("/", response_model=List[CalibrationRecordResponse])
def list_records(
    instrument_id: Optional[int] = Query(None),
    agency_id: Optional[int] = Query(None),
    result: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CalibrationRecord)
    if instrument_id:
        query = query.filter(CalibrationRecord.instrument_id == instrument_id)
    if agency_id:
        query = query.filter(CalibrationRecord.agency_id == agency_id)
    if result:
        query = query.filter(CalibrationRecord.result == result)
    if start_date:
        query = query.filter(CalibrationRecord.actual_date >= start_date)
    if end_date:
        query = query.filter(CalibrationRecord.actual_date <= end_date)
    query = apply_department_filter(query, CalibrationRecord, current_user)
    return query.all()

@router.get("/{record_id}", response_model=CalibrationRecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(CalibrationRecord).filter(CalibrationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="检定记录不存在")
    return record

@router.post("/", response_model=CalibrationRecordResponse)
def create_record(
    record: CalibrationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_record = CalibrationRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/{record_id}", response_model=CalibrationRecordResponse)
def update_record(
    record_id: int,
    record: CalibrationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_record = db.query(CalibrationRecord).filter(CalibrationRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="检定记录不存在")
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
    record = db.query(CalibrationRecord).filter(CalibrationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="检定记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
