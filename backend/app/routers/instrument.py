from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import String
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.instrument import Instrument, InstrumentStatus
from app.models.user import User
from app.schemas import InstrumentCreate, InstrumentUpdate, InstrumentResponse
from app.utils.auth import get_current_user, require_role, apply_department_filter

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
            Instrument.name.ilike(like) |
            Instrument.code.ilike(like) |
            Instrument.extra_data.cast(String).ilike(like)
        )
    query = apply_department_filter(query, Instrument, current_user)
    return query.all()

@router.get("/expiring", response_model=List[InstrumentResponse])
def list_expiring_instruments(
    days: int = Query(30, description="到期预警天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timedelta
    end_date = date.today() + timedelta(days=days)
    query = db.query(Instrument).filter(
        Instrument.next_cal_date.isnot(None),
        Instrument.next_cal_date <= end_date,
        Instrument.status != InstrumentStatus.SCRAPPED
    )
    query = apply_department_filter(query, Instrument, current_user)
    return query.all()

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
    from app.models.instrument import InstrumentCategory
    from app.services.instrument_service import InstrumentService
    data = inst.model_dump()
    cat_name = data.pop("category_name", None)
    if cat_name and not data.get("category_id"):
        cat = db.query(InstrumentCategory).filter(InstrumentCategory.name == cat_name).first()
        if not cat:
            cat = InstrumentCategory(name=cat_name, level=1)
            db.add(cat)
            db.flush()
        data["category_id"] = cat.id
    data.pop("category_name", None)
    db_inst = Instrument(**data)
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
    update_data = inst.model_dump(exclude_unset=True)
    # Merge extra_data instead of replacing
    if "extra_data" in update_data and update_data["extra_data"] is not None:
        existing = db_inst.extra_data or {}
        existing.update(update_data["extra_data"])
        db_inst.extra_data = existing
        del update_data["extra_data"]
    for key, value in update_data.items():
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
