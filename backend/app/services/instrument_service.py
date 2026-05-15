from app.services.base import BaseCRUDService
from app.models.instrument import Instrument, InstrumentCategory, InstrumentStatus
from app.schemas.instrument import InstrumentCreate, InstrumentUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, timedelta


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
