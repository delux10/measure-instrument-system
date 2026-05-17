from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.instrument import Instrument, InstrumentStatus
from app.models.user import User
from app.schemas import InstrumentCreate, InstrumentUpdate, InstrumentResponse
from app.utils.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[InstrumentResponse])
def list_instruments(
    status: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Instrument)
    if status:
        query = query.filter(Instrument.status == status)
    if department_id:
        query = query.filter(Instrument.department_id == department_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            Instrument.name.ilike(like) | Instrument.code.ilike(like) | Instrument.model.ilike(like)
        )
    return query.all()

@router.get("/expiring", response_model=List[InstrumentResponse])
def list_expiring_instruments(
    days: int = Query(30, description="到期预警天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timedelta
    end_date = date.today() + timedelta(days=days)
    return db.query(Instrument).filter(
        Instrument.next_cal_date.isnot(None),
        Instrument.next_cal_date <= end_date,
        Instrument.status != InstrumentStatus.SCRAPPED
    ).all()

@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument(instrument_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inst = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="仪器不存在")
    return inst

@router.post("/", response_model=InstrumentResponse)
def create_instrument(
    inst: InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    existing = db.query(Instrument).filter(Instrument.code == inst.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="仪器编号已存在")
    db_inst = Instrument(**inst.model_dump())
    db.add(db_inst)
    db.commit()
    db.refresh(db_inst)
    return db_inst

@router.put("/{instrument_id}", response_model=InstrumentResponse)
def update_instrument(
    instrument_id: int,
    inst: InstrumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_inst = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not db_inst:
        raise HTTPException(status_code=404, detail="仪器不存在")
    for key, value in inst.model_dump(exclude_unset=True).items():
        setattr(db_inst, key, value)
    db.commit()
    db.refresh(db_inst)
    return db_inst

@router.delete("/{instrument_id}")
def delete_instrument(
    instrument_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    inst = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="仪器不存在")
    db.delete(inst)
    db.commit()
    return {"message": "删除成功"}


@router.post("/import")
def import_instruments(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    from app.services.instrument_service import InstrumentService
    from app.config import settings

    content = file.file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE // (1024*1024)}MB)")
    svc = InstrumentService()
    return svc.batch_import(db, content, file.filename or "")
