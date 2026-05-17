from app.services.base import BaseCRUDService
from app.models.instrument import Instrument, InstrumentCategory, InstrumentStatus
from app.schemas.instrument import (
    InstrumentCreate, InstrumentUpdate,
    ImportRowError, ImportResultResponse,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, datetime
from datetime import timedelta
from typing import Optional, List, Tuple, Dict
from io import BytesIO
import openpyxl


MES_COLUMN_MAP = {
    "仪器编号": "code",
    "管理编号": "code",
    "资产编号": "code",
    "仪器名称": "name",
    "设备名称": "name",
    "名称": "name",
    "型号规格": "model",
    "型号": "model",
    "规格": "model",
    "出厂编号": "serial_no",
    "序列号": "serial_no",
    "出厂编号/序列号": "serial_no",
    "测量范围": "range_value",
    "量程": "range_value",
    "测量范围/量程": "range_value",
    "精度等级": "accuracy",
    "精度": "accuracy",
    "不确定度": "accuracy",
    "精度等级/不确定度": "accuracy",
    "分度值": "scale_interval",
    "出厂日期": "manufacture_date",
    "生产厂家": "manufacturer",
    "厂家": "manufacturer",
    "制造厂家": "manufacturer",
    "制造商": "manufacturer",
    "责任人": "keeper",
    "保管人": "keeper",
    "保管员": "keeper",
    "负责人": "keeper",
    "检定/校准单位": "cal_agency",
    "检定单位": "cal_agency",
    "校准单位": "cal_agency",
    "检定机构": "cal_agency",
    "证书编号": "certificate_no",
    "检定日期": "last_cal_date",
    "检定时间": "last_cal_date",
    "上次检定日期": "last_cal_date",
    "有效期": "next_cal_date",
    "有效期至": "next_cal_date",
    "下次检定日期": "next_cal_date",
    "证书确认": "cert_confirmed",
    "计量特性": "metrology_characteristic",
    "计量特性/技术指标": "metrology_characteristic",
    "状态": "status",
    "仪器状态": "status",
    "使用状态": "status",
    "使用部门": "department_name",
    "部门": "department_name",
    "所属部门": "department_name",
    "管理部门": "department_name",
    "安装地点": "location",
    "存放地点": "location",
    "使用地点": "location",
    "存放位置": "location",
    "备注": "remark",
    "检定周期": "calibration_cycle",
    "检定周期(月)": "calibration_cycle",
    "周期": "calibration_cycle",
    "仪器分类": "category_name",
    "分类": "category_name",
    "资产原值": "price",
    "原值": "price",
    "购入日期": "purchase_date",
    "检定方式": "cal_method",
    "送检方式": "cal_method",
}

STATUS_MAP = {
    "在用": "in_use",
    "停用": "stopped",
    "封存": "idle",
    "报废": "scrapped",
    "送检": "calibrating",
    "维修": "repair",
}


def _parse_date(val: str) -> Optional[date]:
    val = str(val).strip()
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y年%m月%d日", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    try:
        serial = float(val)
        if 1 <= serial <= 2958465:
            return date(1899, 12, 30) + timedelta(days=int(serial))
    except ValueError:
        pass
    return None


def validate_row(
    values: dict,
    existing_codes: set,
    cat_by_name: dict,
    cat_by_path: dict,
    departments: dict,
) -> List[ImportRowError]:
    """Pure validation — no DB access. Returns empty list if row is valid."""
    errors = []

    code = values.get("code", "")
    if not code:
        errors.append(ImportRowError(row=0, field="仪器编号", message="缺少 仪器编号（管理编号）"))
        return errors  # can't proceed without code

    if code in existing_codes:
        errors.append(ImportRowError(row=0, field="仪器编号", message=f"仪器编号「{code}」已存在"))

    name = values.get("name", "")
    if not name:
        errors.append(ImportRowError(row=0, field="仪器名称", message="缺少 仪器名称"))

    model = values.get("model", "")
    if not model:
        errors.append(ImportRowError(row=0, field="型号规格", message="缺少 型号规格"))

    cat_name = values.get("category_name", "")
    if not cat_name:
        errors.append(ImportRowError(row=0, field="仪器分类", message="缺少 仪器分类"))
    else:
        cat_id = cat_by_name.get(cat_name)
        if cat_id is None:
            cat_id = cat_by_path.get(cat_name)
        if cat_id is None:
            errors.append(ImportRowError(row=0, field="仪器分类", message=f"分类「{cat_name}」不存在"))

    # Date field validation (warn only — don't block)
    for date_field in ("manufacture_date", "last_cal_date", "next_cal_date", "purchase_date"):
        v = values.get(date_field)
        if v and not isinstance(v, date):
            parsed = _parse_date(str(v))
            if parsed is None:
                errors.append(ImportRowError(row=0, field=date_field, message=f"日期格式无法识别: {v}"))

    # Price validation
    price_raw = values.get("price")
    if price_raw:
        try:
            float(str(price_raw).replace(",", "").replace("，", ""))
        except ValueError:
            errors.append(ImportRowError(row=0, field="price", message=f"价格格式无法识别: {price_raw}"))

    # Department — soft fail (warn but don't block)
    dept_name = values.get("department_name")
    if dept_name and dept_name not in departments:
        errors.append(ImportRowError(row=0, field="使用部门", message=f"部门「{dept_name}」不存在"))

    return errors


def build_instrument_from_values(
    values: dict,
    departments: dict,
    cat_by_name: dict,
    cat_by_path: dict,
) -> Instrument:
    values = dict(values)  # copy to prevent mutation of caller's dict
    dept_name = values.pop("department_name", None)
    dept_id = departments.get(dept_name) if dept_name else None

    cat_name = values.pop("category_name", None)
    cat_id = None
    if cat_name:
        cat_id = cat_by_name.get(cat_name)
        if cat_id is None:
            cat_id = cat_by_path.get(cat_name)

    status_raw = values.get("status", "")
    if status_raw and status_raw in STATUS_MAP:
        values["status"] = STATUS_MAP[status_raw]

    cycle_raw = values.get("calibration_cycle")
    if cycle_raw:
        cycle_str = str(cycle_raw).replace("个月", "").replace("月", "").strip()
        try:
            values["calibration_cycle"] = int(float(cycle_str))
        except ValueError:
            values.pop("calibration_cycle", None)

    for date_field in ("manufacture_date", "last_cal_date", "next_cal_date", "purchase_date"):
        v = values.get(date_field)
        if v:
            parsed = _parse_date(v) if not isinstance(v, date) else v
            if parsed:
                values[date_field] = parsed
            else:
                values.pop(date_field, None)

    price_raw = values.get("price")
    if price_raw:
        try:
            values["price"] = float(str(price_raw).replace(",", "").replace("，", ""))
        except ValueError:
            values.pop("price", None)

    if not values.get("next_cal_date"):
        last_cal = values.get("last_cal_date")
        cycle = values.get("calibration_cycle")
        if last_cal and isinstance(last_cal, date) and cycle:
            total_months = last_cal.year * 12 + last_cal.month - 1 + cycle
            next_year = total_months // 12
            next_month = total_months % 12 + 1
            next_day = min(last_cal.day, 28)
            values["next_cal_date"] = date(next_year, next_month, next_day)

    return Instrument(
        code=values.get("code", ""),
        name=values.get("name", ""),
        model=values.get("model"),
        serial_no=values.get("serial_no"),
        category_id=cat_id,
        range_value=values.get("range_value"),
        accuracy=values.get("accuracy"),
        scale_interval=values.get("scale_interval"),
        manufacture_date=values.get("manufacture_date"),
        manufacturer=values.get("manufacturer"),
        purchase_date=values.get("purchase_date"),
        price=values.get("price"),
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
        cal_method=values.get("cal_method"),
        remark=values.get("remark"),
    )


class InstrumentCategoryService(BaseCRUDService):
    def __init__(self):
        super().__init__(InstrumentCategory, "仪器分类")

    def create(self, db: Session, schema):
        parent_id = getattr(schema, 'parent_id', None)
        if parent_id:
            parent = db.query(InstrumentCategory).filter(InstrumentCategory.id == parent_id).first()
            if not parent:
                raise HTTPException(status_code=400, detail="父分类不存在")
            level = parent.level + 1
        else:
            level = 1
        obj = InstrumentCategory(name=schema.name, parent_id=parent_id, level=level)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id: int):
        obj = self.get(db, id)
        if db.query(InstrumentCategory).filter(InstrumentCategory.parent_id == id).first():
            raise HTTPException(status_code=400, detail="请先删除子分类")
        db.delete(obj)
        db.commit()


class InstrumentService(BaseCRUDService):
    def __init__(self):
        super().__init__(Instrument, "仪器")

    def create(self, db: Session, schema: InstrumentCreate):
        existing = db.query(Instrument).filter(Instrument.code == schema.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="仪器编号已存在")
        return super().create(db, schema)

    def list_expiring(self, db: Session, days: int = 30):
        end_date = date.today() + timedelta(days=days)
        items = db.query(Instrument).filter(
            Instrument.next_cal_date.isnot(None),
            Instrument.next_cal_date <= end_date,
            Instrument.status != InstrumentStatus.SCRAPPED
        ).all()
        return items

    def batch_import(
        self,
        db: Session,
        file_content: bytes,
        filename: str,
    ) -> ImportResultResponse:
        if not filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="仅支持 .xlsx / .xls 格式")

        try:
            wb = openpyxl.load_workbook(BytesIO(file_content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无法解析 Excel 文件: {str(e)}")

        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            raise HTTPException(status_code=400, detail="文件为空或仅包含表头")

        # Parse header -> column map
        headers = [str(h).strip() if h is not None else "" for h in rows[0]]
        col_map: Dict[int, str] = {}
        for idx, h in enumerate(headers):
            if h and h in MES_COLUMN_MAP:
                col_map[idx] = MES_COLUMN_MAP[h]

        if not col_map:
            raise HTTPException(
                status_code=400,
                detail=f"未识别到任何有效列名。表头: {', '.join(headers[:15])}..."
            )

        # Preload lookups
        from app.models.department import Department
        departments = {d.name: d.id for d in db.query(Department).all()}

        categories = db.query(InstrumentCategory).all()
        cat_by_name: dict = {c.name: c.id for c in categories}
        cat_by_path: dict = {}
        for c in categories:
            parts = [c.name]
            parent = c.parent
            visited = set()
            while parent and parent.id not in visited:
                visited.add(parent.id)
                parts.insert(0, parent.name)
                parent = parent.parent
            cat_by_path["/".join(parts)] = c.id

        existing_codes: set = {c for (c,) in db.query(Instrument.code).all()}

        # Pass 1: parse and validate all rows
        valid_rows: list = []
        all_errors: list = []
        data_rows = 0

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

            data_rows += 1
            row_errors = validate_row(values, existing_codes, cat_by_name, cat_by_path, departments)
            if row_errors:
                for err in row_errors:
                    err.row = row_idx
                all_errors.extend(row_errors)
            else:
                valid_rows.append((row_idx, values))

        failure_count = len(all_errors)

        # Pass 2: batch-insert valid rows
        BATCH_SIZE = 100
        success_count = 0

        for batch_start in range(0, len(valid_rows), BATCH_SIZE):
            batch = valid_rows[batch_start:batch_start + BATCH_SIZE]
            try:
                for row_idx, values in batch:
                    inst = build_instrument_from_values(
                        values, departments, cat_by_name, cat_by_path
                    )
                    db.add(inst)
                    existing_codes.add(inst.code)
                db.commit()
                success_count += len(batch)
            except Exception:
                db.rollback()
                # Fall back to row-by-row for this batch to isolate the failing row
                for row_idx, values in batch:
                    try:
                        inst = build_instrument_from_values(
                            values, departments, cat_by_name, cat_by_path
                        )
                        db.add(inst)
                        db.commit()
                        existing_codes.add(inst.code)
                        success_count += 1
                    except Exception as row_e:
                        db.rollback()
                        all_errors.append(ImportRowError(
                            row=row_idx,
                            message=f"数据库异常: {str(row_e)}"
                        ))
                        failure_count += 1

        message = f"导入完成：成功 {success_count} 条，失败 {failure_count} 条"
        return ImportResultResponse(
            total_rows=data_rows,
            success_count=success_count,
            failure_count=failure_count,
            errors=all_errors[:200],
            message=message,
        )
