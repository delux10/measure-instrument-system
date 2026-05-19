"""检定管理路由"""
import re
from calendar import monthrange
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
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

# ── 自动生成检定计划 ──
def _parse_date(val) -> date | None:
    """尝试解析各种日期格式"""
    if not val:
        return None
    s = str(val).strip()
    if not s:
        return None
    formats = [
        r"(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})日?",
        r"(\d{4})[年/\-.](\d{1,2})[月]?",
    ]
    for pattern in formats:
        m = re.search(pattern, s)
        if m:
            try:
                y, mo = int(m.group(1)), int(m.group(2))
                d = int(m.group(3)) if m.lastindex and m.lastindex >= 3 else 1
                return date(y, mo, d)
            except ValueError:
                continue
    return None

@router.post("/generate-plan")
def generate_plan(
    year_month: str = Query(..., description="年月，格式 YYYY-MM"),
    department_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager", "dept_measurer"])),
):
    try:
        year, month = map(int, year_month.split("-"))
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
    except Exception:
        raise HTTPException(400, detail="月份格式错误，请使用 YYYY-MM 格式")

    query = apply_department_filter(db.query(Instrument), Instrument, current_user)
    if department_id:
        query = query.filter(Instrument.department_id == department_id)
    instruments = query.all()

    created = 0
    skipped = 0
    skipped_existing = 0
    errors = []

    for inst in instruments:
        raw = (inst.fields or {}).get("下次检验日期")
        parsed = _parse_date(raw)
        if not parsed:
            skipped += 1
            continue
        if not (start_date <= parsed <= end_date):
            skipped += 1
            continue

        # 检查是否已存在该仪器+该计划日期的记录
        existing = db.query(CalibrationRecord).filter(
            CalibrationRecord.instrument_id == inst.id,
            CalibrationRecord.plan_date == parsed,
        ).first()
        if existing:
            skipped_existing += 1
            continue

        # 尝试匹配检测院
        agency_id = None
        agency_name = (inst.fields or {}).get("确认单位", "")
        if agency_name:
            agency = db.query(CalibrationAgency).filter(
                CalibrationAgency.name.ilike(f"%{agency_name}%")
            ).first()
            if agency:
                agency_id = agency.id

        rec = CalibrationRecord(
            instrument_id=inst.id,
            department_id=inst.department_id,
            plan_date=parsed,
            agency_id=agency_id,
            fields={
                "确认单位": agency_name,
                "检定方式": (inst.fields or {}).get("检定方式", ""),
                "有效日期": (inst.fields or {}).get("有效日期", ""),
                "确认间隔": (inst.fields or {}).get("确认间隔", ""),
            },
        )
        db.add(rec)
        created += 1

    db.commit()
    log(db, current_user.id, "generate", "calibration_plan",
        summary=f"生成 {year_month} 检定计划：创建 {created}，跳过无日期 {skipped}，跳过已存在 {skipped_existing}")

    return {
        "data": {
            "created": created,
            "skipped_invalid_date": skipped,
            "skipped_existing": skipped_existing,
            "errors": errors,
            "month": year_month,
        }
    }

# ── 删除检定记录 ──
@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(["admin", "system_manager"]))):
    rec = db.query(CalibrationRecord).filter(CalibrationRecord.id == record_id).first()
    if not rec:
        raise HTTPException(404, detail="检定记录不存在")
    log(db, current_user.id, "delete", "calibration_record", rec.id, summary=f"删除检定记录")
    db.delete(rec)
    db.commit()
    return {"data": None}

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
