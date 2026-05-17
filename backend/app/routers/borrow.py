from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.borrow import BorrowRecord, BorrowStatus
from app.models.user import User
from app.schemas import BorrowCreate, BorrowUpdate, BorrowResponse
from app.utils.auth import get_current_user, require_role, apply_department_filter

router = APIRouter()

@router.get("/", response_model=List[BorrowResponse])
def list_borrows(
    status: Optional[str] = Query(None),
    instrument_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(BorrowRecord)
    if status:
        query = query.filter(BorrowRecord.status == status)
    if instrument_id:
        query = query.filter(BorrowRecord.instrument_id == instrument_id)
    query = apply_department_filter(query, BorrowRecord, current_user)
    return query.all()

@router.get("/{borrow_id}", response_model=BorrowResponse)
def get_borrow(borrow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借用记录不存在")
    return record

@router.post("/", response_model=BorrowResponse)
def create_borrow(
    borrow: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_record = BorrowRecord(**borrow.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/{borrow_id}/return", response_model=BorrowResponse)
def return_instrument(
    borrow_id: int,
    borrow: BorrowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import date
    db_record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="借用记录不存在")
    db_record.status = BorrowStatus.RETURNED
    db_record.actual_return_date = borrow.actual_return_date or date.today()
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{borrow_id}")
def delete_borrow(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借用记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
