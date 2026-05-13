from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.instrument import InstrumentCategory
from app.schemas import InstrumentCategoryCreate, InstrumentCategoryResponse
from app.utils.auth import get_current_user, require_role
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[InstrumentCategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(InstrumentCategory).filter(InstrumentCategory.parent_id.is_(None)).all()
    return categories

@router.get("/all", response_model=List[InstrumentCategoryResponse])
def list_all_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(InstrumentCategory).all()
    return categories

@router.get("/{category_id}", response_model=InstrumentCategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(InstrumentCategory).filter(InstrumentCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    return cat

@router.post("/", response_model=InstrumentCategoryResponse)
def create_category(
    cat: InstrumentCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    if cat.parent_id:
        parent = db.query(InstrumentCategory).filter(InstrumentCategory.id == cat.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父分类不存在")
        new_level = parent.level + 1
    else:
        new_level = 1
    db_cat = InstrumentCategory(name=cat.name, parent_id=cat.parent_id, level=new_level)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.put("/{category_id}", response_model=InstrumentCategoryResponse)
def update_category(
    category_id: int,
    cat: InstrumentCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_cat = db.query(InstrumentCategory).filter(InstrumentCategory.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    db_cat.name = cat.name
    db_cat.parent_id = cat.parent_id
    if cat.parent_id:
        parent = db.query(InstrumentCategory).filter(InstrumentCategory.id == cat.parent_id).first()
        if parent:
            db_cat.level = parent.level + 1
    else:
        db_cat.level = 1
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    cat = db.query(InstrumentCategory).filter(InstrumentCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    if db.query(InstrumentCategory).filter(InstrumentCategory.parent_id == category_id).first():
        raise HTTPException(status_code=400, detail="请先删除子分类")
    db.delete(cat)
    db.commit()
    return {"message": "删除成功"}
