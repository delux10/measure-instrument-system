"""检定管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.models import Instrument, CalibrationRecord, CalibrationAgency, User
from app.schemas import CalibrationRecordCreate, CalibrationRecordUpdate, CalibrationAgencyCreate
from app.utils.auth import get_current_user, require_role, apply_department_filter
from app.utils.audit import log

router = APIRouter()

# ── 检定记录列表 ──
@router.get("/records")
def list_records(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                 instrument_id: int = Query(None), status: str = Query(None),
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = apply_department_filter(db.query(CalibrationRecord), CalibrationRecord, current_user)
    if instrument_id: query = query.filter(CalibrationRecord.instrument_id == instrument_id)
    if status == "pending": query = query.filter(CalibrationRecord.actual_date.is_(None))
    elif status == "done": query = query.filter(CalibrationRecord.actual_date.isnot(None))
    total = query.count()
    items = query.order_by(CalibrationRecord.plan_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    from app.models import Instrument as Inst
    insts = {}
    def fmt(r):
        if r.instrument_id and r.instrument_id not in insts:
            inst = db.query(Inst).filter(Inst.id == r.instrument_id).first()
            insts[r.instrument_id] = inst
        inst = insts.get(r.instrument_id)
        return {
            "id": r.id, "instrument_id": r.instrument_id,
            "instrument_name": inst.name if inst else None, "instrument_code": inst.code if inst else None,
            "agency_id": r.agency_id, "plan_date": str(r.plan_date) if r.plan_date else None,
            "actual_date": str(r.actual_date) if r.actual_date else None,
            "result": r.result, "fields": r.fields or {},
            "created_at": str(r.created_at) if r.created_at else None,
        }
    return {"data": [fmt(r) for r in items], "meta": {"total": total, "page": page, "page_size": page_size}}

# ── 创建检定记录 ──
@router.post("/records")
def create_record(body: CalibrationRecordCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(["admin", "system_manager", "dept_measurer"]))):
    inst = db.query(Instrument).filter(Instrument.id == body.instrument_id).first()
    if not inst: raise HTTPException(404, detail="仪器不存在")
    rec = CalibrationRecord(instrument_id=body.instrument_id, agency_id=body.agency_id,
                            plan_date=body.plan_date, actual_date=body.actual_date,
                            result=body.result, department_id=body.department_id or current_user.department_id,
                            fields=body.fields or {})
    db.add(rec); db.flush()
    log(db, current_user.id, "create", "calibration", rec.id, summary=f"新增检定记录")
    db.commit(); db.refresh(rec)
    return {"data": {"id": rec.id}}

# ── 更新检定记录 ──
@router.put("/records/{record_id}")
def update_record(record_id: int, body: CalibrationRecordUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(["admin", "system_manager", "dept_measurer"]))):
    rec = db.query(CalibrationRecord).filter(CalibrationRecord.id == record_id).first()
    if not rec: raise HTTPException(404, detail="检定记录不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None: setattr(rec, k, v)
    if body.actual_date and not rec.actual_date:
        inst = db.query(Instrument).filter(Instrument.id == rec.instrument_id).first()
        if inst and body.actual_date:
            from datetime import datetime as dt
            inst.fields = {**(inst.fields or {}), "最近检定日期": str(body.actual_date)}
    log(db, current_user.id, "update", "calibration", rec.id, summary=f"更新检定记录")
    db.commit(); db.refresh(rec)
    return {"data": {"id": rec.id}}

# ── 到期预警 ──
@router.get("/expiring")
def expiring(days: int = Query(30), db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    end = date.today() + timedelta(days=days)
    query = db.query(CalibrationRecord).filter(
        CalibrationRecord.plan_date <= end, CalibrationRecord.actual_date.is_(None)
    )
    query = apply_department_filter(query, CalibrationRecord, current_user)
    return {"data": [{"id": r.id, "instrument_id": r.instrument_id, "plan_date": str(r.plan_date) if r.plan_date else None} for r in query.all()], "meta": None}

# ── 检测院 CRUD ──
@router.get("/agencies")
def list_agencies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"data": [{"id": a.id, "name": a.name, "contact_person": a.contact_person, "contact_phone": a.contact_phone} for a in db.query(CalibrationAgency).all()], "meta": None}

@router.post("/agencies")
def create_agency(body: CalibrationAgencyCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(["admin", "system_manager"]))):
    a = CalibrationAgency(**body.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return {"data": {"id": a.id, "name": a.name}}
