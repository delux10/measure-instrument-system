from typing import TypeVar, Optional, List, Tuple, Type
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import BaseModel

ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseCRUDService:
    """通用 CRUD 服务基类

    子类覆盖 create / update / delete 以加入业务校验逻辑。
    """

    def __init__(self, model: Type, name: str = "记录"):
        self.model = model
        self.name = name

    def list(
        self, db: Session, *, page: int = 1, page_size: int = 20, **filters
    ) -> Tuple[List, int]:
        query = db.query(self.model)
        for attr, value in filters.items():
            if value is not None and hasattr(self.model, attr):
                col = getattr(self.model, attr)
                if isinstance(value, str):
                    query = query.filter(col.ilike(f"%{value}%"))
                else:
                    query = query.filter(col == value)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get(self, db: Session, id: int):
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.name}不存在")
        return obj

    def create(self, db: Session, schema: BaseModel):
        obj = self.model(**schema.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, id: int, schema: BaseModel):
        obj = self.get(db, id)
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id: int):
        obj = self.get(db, id)
        db.delete(obj)
        db.commit()
