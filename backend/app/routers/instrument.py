from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from io import BytesIO
import openpyxl
from app.database import get_db
from app.models.instrument import Instrument, InstrumentStatus
from app.models.department import Department
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


# MES 列名 → 模型字段映射
MES_COLUMN_MAP = {
    "仪器编号": "code",
    "仪器名称": "name",
    "型号规格": "model",
    "型号": "model",
    "规格": "model",
    "出厂编号": "serial_no",
    "测量范围": "range_value",
    "精度等级": "accuracy",
    "精度": "accuracy",
    "不确定度": "accuracy",
    "精度等级/不确定度": "accuracy",
    "分度值": "scale_interval",
    "出厂日期": "manufacture_date",
    "生产厂家": "manufacturer",
    "厂家": "manufacturer",
    "责任人": "keeper",
    "保管人": "keeper",
    "检定/校准单位": "cal_agency",
    "检定单位": "cal_agency",
    "校准单位": "cal_agency",
    "证书编号": "certificate_no",
    "检定日期": "last_cal_date",
    "有效期": "next_cal_date",
    "有效期至": "next_cal_date",
    "证书确认": "cert_confirmed",
    "计量特性": "metrology_characteristic",
    "状态": "status",
    "使用部门": "department_name",
    "部门": "department_name",
    "安装地点": "location",
    "存放地点": "location",
    "备注": "remark",
    "检定周期": "calibration_cycle",
}

STATUS_MAP = {
    "在用": "in_use",
    "停用": "stopped",
    "封存": "idle",
    "报废": "scrapped",
    "送检": "calibrating",
    "维修": "repair",
}


@router.post("/import")
def import_instruments(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx / .xls 格式")

    try:
        content = file.file.read()
        wb = openpyxl.load_workbook(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法解析 Excel 文件: {str(e)}")

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="文件为空或仅包含表头")

    # 解析表头，建立列索引映射
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    col_map = {}
    for idx, h in enumerate(headers):
        if h and h in MES_COLUMN_MAP:
            col_map[idx] = MES_COLUMN_MAP[h]

    if not col_map:
        raise HTTPException(
            status_code=400,
            detail=f"未识别到任何有效列名。表头: {', '.join(headers[:15])}..."
        )

    # 预加载部门映射
    departments = {d.name: d.id for d in db.query(Department).all()}

    # 预加载已有编号
    existing_codes = {c for (c,) in db.query(Instrument.code).all()}

    success_count = 0
    skip_count = 0
    errors = []

    for row_idx, row in enumerate(rows[1:], start=2):
        values = {}
        for col_idx, field_name in col_map.items():
            val = row[col_idx] if col_idx < len(row) else None
            if val is not None:
                val_str = str(val).strip()
                if not val_str or val_str in ("None", "/", "-"):
                    continue
                values[field_name] = val_str

        if not values:
            continue

        code = values.get("code", "")
        if not code:
            errors.append({"row": row_idx, "msg": "仪器编号为空，跳过"})
            skip_count += 1
            continue
        if code in existing_codes:
            errors.append({"row": row_idx, "msg": f"仪器编号「{code}」已存在，跳过"})
            skip_count += 1
            continue

        # 部门名称 → ID
        dept_name = values.pop("department_name", None)
        dept_id = departments.get(dept_name) if dept_name else None

        # 状态映射
        status_raw = values.get("status", "")
        if status_raw and status_raw in STATUS_MAP:
            values["status"] = STATUS_MAP[status_raw]

        # 日期解析
        for date_field in ("manufacture_date", "last_cal_date", "next_cal_date"):
            v = values.get(date_field)
            if v:
                parsed = _parse_date(v)
                if parsed:
                    values[date_field] = parsed
                else:
                    values.pop(date_field, None)

        # 数值解析
        cycle = values.get("calibration_cycle")
        if cycle:
            try:
                values["calibration_cycle"] = int(float(cycle))
            except ValueError:
                values.pop("calibration_cycle", None)

        try:
            inst = Instrument(
                code=code,
                name=values.get("name", ""),
                model=values.get("model"),
                serial_no=values.get("serial_no"),
                range_value=values.get("range_value"),
                accuracy=values.get("accuracy"),
                scale_interval=values.get("scale_interval"),
                manufacture_date=values.get("manufacture_date"),
                manufacturer=values.get("manufacturer"),
                keeper=values.get("keeper"),
                department_id=dept_id,
                location=values.get("location"),
                cal_agency=values.get("cal_agency"),
                certificate_no=values.get("certificate_no"),
                cert_confirmed=values.get("cert_confirmed"),
                metrology_characteristic=values.get("metrology_characteristic"),
                status=values.get("status", "in_use"),
                calibration_cycle=values.get("calibration_cycle"),
                last_cal_date=values.get("last_cal_date"),
                next_cal_date=values.get("next_cal_date"),
                remark=values.get("remark"),
            )
            db.add(inst)
            existing_codes.add(code)
            success_count += 1
        except Exception as e:
            errors.append({"row": row_idx, "msg": f"数据异常: {str(e)}"})
            skip_count += 1

    db.commit()

    return {
        "message": f"导入完成：成功 {success_count} 条，跳过 {skip_count} 条",
        "success_count": success_count,
        "skip_count": skip_count,
        "total": len(rows) - 1,
        "errors": errors[:50],
    }


def _parse_date(val: str) -> Optional[date]:
    """尝试多种日期格式"""
    val = str(val).strip()
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y年%m月%d日", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    # 尝试 Excel 序列号
    try:
        serial = float(val)
        if 1 <= serial <= 2958465:
            from datetime import date as date_type, timedelta
            return date_type(1899, 12, 30) + timedelta(days=int(serial))
    except ValueError:
        pass
    return None
