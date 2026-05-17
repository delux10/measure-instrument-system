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
from typing import Optional, List, Dict
from io import BytesIO
import openpyxl


# Maps Excel header names → fixed Instrument column keys.
# Only columns that have dedicated DB columns (code, name, FK lookups, calibration dates).
FIXED_COLUMN_NAMES = {"code", "name", "department_name", "category_name",
                       "last_cal_date", "next_cal_date", "calibration_cycle"}

STATUS_MAP = {
    "在用": "in_use",
    "停用": "stopped",
    "封存": "idle",
    "报废": "scrapped",
    "送检": "calibrating",
    "维修": "repair",
}

# Recognized header aliases for the few fixed columns we extract
HEADER_ALIASES = {
    "code": ["仪器编号", "管理编号", "资产编号"],
    "name": ["仪器名称", "计量设备名称", "设备名称", "名称"],
    "department_name": ["使用部门", "部门", "所属部门", "管理部门"],
    "category_name": ["仪器分类", "分类"],
    "last_cal_date": ["检定日期", "检定时间", "上次检定日期", "确认日期"],
    "next_cal_date": ["有效期", "有效期至", "下次检定日期", "有效日期", "下次检验日期"],
    "calibration_cycle": ["检定周期", "检定周期(月)", "周期", "确认间隔"],
}


def _build_header_map(headers: list) -> Dict[str, str]:
    """Build a reverse map: header text -> fixed field name (or None for extra_data)."""
    result = {}
    for h in headers:
        h = str(h).strip() if h else ""
        if not h:
            continue
        matched = None
        for field_name, aliases in HEADER_ALIASES.items():
            if h in aliases:
                matched = field_name
                break
        result[h] = matched  # None means this header goes to extra_data
    return result


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
) -> List[ImportRowError]:
    """Validate only the essential fixed fields. Everything else is free-form."""
    errors = []

    code = values.get("code", "")
    if not code:
        errors.append(ImportRowError(row=0, field="仪器编号", message="缺少 仪器编号（管理编号）"))
        return errors

    if code in existing_codes:
        errors.append(ImportRowError(row=0, field="仪器编号", message=f"仪器编号「{code}」已存在"))

    name = values.get("name", "")
    if not name:
        errors.append(ImportRowError(row=0, field="仪器名称", message="缺少 仪器名称"))

    cat_name = values.get("category_name", "")
    if not cat_name:
        errors.append(ImportRowError(row=0, field="仪器分类", message="缺少 仪器分类"))

    return errors


def _build_instrument(
    values: dict,
    extra_data: dict,
    departments: dict,
    cat_by_name: dict,
    cat_by_path: dict,
) -> Instrument:
    dept_name = values.get("department_name")
    dept_id = departments.get(dept_name) if dept_name else None

    cat_name = values.get("category_name")
    cat_id = None
    if cat_name:
        cat_id = cat_by_name.get(cat_name) or cat_by_path.get(cat_name)

    status = values.get("status", "in_use")
    if status in STATUS_MAP:
        status = STATUS_MAP[status]

    cycle = values.get("calibration_cycle")
    if cycle is not None:
        try:
            cycle = int(float(str(cycle).replace("个月", "").replace("月", "").strip()))
        except (ValueError, TypeError):
            cycle = None

    last_cal = values.get("last_cal_date")
    if last_cal and not isinstance(last_cal, date):
        last_cal = _parse_date(str(last_cal))
    next_cal = values.get("next_cal_date")
    if next_cal and not isinstance(next_cal, date):
        next_cal = _parse_date(str(next_cal))

    if not next_cal and last_cal and isinstance(last_cal, date) and cycle:
        total_months = last_cal.year * 12 + last_cal.month - 1 + cycle
        next_cal = date(total_months // 12, total_months % 12 + 1, min(last_cal.day, 28))

    return Instrument(
        code=values.get("code", ""),
        name=values.get("name", ""),
        category_id=cat_id,
        department_id=dept_id,
        status=status,
        calibration_cycle=cycle,
        last_cal_date=last_cal,
        next_cal_date=next_cal,
        extra_data=extra_data,
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

        magic = file_content[:4]
        if magic[:2] == b'\xd0\xcf':
            raise HTTPException(
                status_code=400,
                detail="不支持旧版 .xls 格式，请在 Excel 中另存为「Excel 工作簿 (.xlsx)」格式后重新上传"
            )
        if magic != b'PK\x03\x04':
            raise HTTPException(status_code=400, detail="文件格式不正确，请上传有效的 .xlsx 文件")

        try:
            wb = openpyxl.load_workbook(BytesIO(file_content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无法解析 Excel 文件: {str(e)}")

        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            raise HTTPException(status_code=400, detail="文件为空或仅包含表头")

        headers = [str(h).strip() if h is not None else "" for h in rows[0]]
        header_map = _build_header_map(headers)

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

        # Pass 1: parse and validate
        valid_rows: list = []
        all_errors: list = []
        data_rows = 0

        for row_idx, row in enumerate(rows[1:], start=2):
            values = {}
            extra = {}
            has_any = False
            for col_idx, header_text in enumerate(headers):
                if not header_text:
                    continue
                val = row[col_idx] if col_idx < len(row) else None
                if val is None:
                    continue
                # Convert to a clean value (string, number, or date)
                if isinstance(val, datetime):
                    val = val.date()
                elif isinstance(val, str):
                    val = val.strip()
                    if not val or val in ("None", "/", "-"):
                        continue
                has_any = True

                fixed_field = header_map.get(header_text)
                if fixed_field:
                    values[fixed_field] = val
                else:
                    extra[header_text] = val

            if not has_any:
                continue

            data_rows += 1
            row_errors = validate_row(values, existing_codes, cat_by_name, cat_by_path)
            if row_errors:
                for err in row_errors:
                    err.row = row_idx
                all_errors.extend(row_errors)
            else:
                valid_rows.append((row_idx, values, extra))

        failure_count = len(all_errors)

        def ensure_department(dept_name: str):
            if dept_name in departments:
                return departments[dept_name]
            dept = Department(name=dept_name, level=1)
            db.add(dept)
            db.flush()
            departments[dept_name] = dept.id
            return dept.id

        def ensure_category(cat_name: str):
            if cat_name in cat_by_name:
                return cat_by_name[cat_name]
            if cat_name in cat_by_path:
                return cat_by_path[cat_name]
            cat = InstrumentCategory(name=cat_name, level=1)
            db.add(cat)
            db.flush()
            cat_by_name[cat_name] = cat.id
            return cat.id

        # Pass 2: batch-insert
        BATCH_SIZE = 100
        success_count = 0

        for batch_start in range(0, len(valid_rows), BATCH_SIZE):
            batch = valid_rows[batch_start:batch_start + BATCH_SIZE]
            try:
                for row_idx, values, extra in batch:
                    dept_name = values.get("department_name")
                    if dept_name:
                        ensure_department(dept_name)
                    cat_name = values.get("category_name")
                    if cat_name:
                        ensure_category(cat_name)
                    inst = _build_instrument(values, extra, departments, cat_by_name, cat_by_path)
                    db.add(inst)
                    existing_codes.add(inst.code)
                db.commit()
                success_count += len(batch)
            except Exception:
                db.rollback()
                for row_idx, values, extra in batch:
                    try:
                        dept_name = values.get("department_name")
                        if dept_name:
                            ensure_department(dept_name)
                        cat_name = values.get("category_name")
                        if cat_name:
                            ensure_category(cat_name)
                        inst = _build_instrument(values, extra, departments, cat_by_name, cat_by_path)
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
