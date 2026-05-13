from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.supervision import SupervisionTemplate, SupervisionTemplateItem
from app.models.user import User
from app.schemas import (
    SupervisionTemplateCreate, SupervisionTemplateUpdate, SupervisionTemplateResponse,
    SupervisionTemplateItemCreate, SupervisionTemplateItemUpdate, SupervisionTemplateItemResponse
)
from app.utils.auth import get_current_user, require_role

router = APIRouter()

# === Template CRUD ===

@router.get("/", response_model=List[SupervisionTemplateResponse])
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SupervisionTemplate).all()

@router.get("/{template_id}", response_model=SupervisionTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tpl = db.query(SupervisionTemplate).filter(SupervisionTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return tpl

@router.post("/", response_model=SupervisionTemplateResponse)
def create_template(
    tpl: SupervisionTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_tpl = SupervisionTemplate(**tpl.model_dump())
    db.add(db_tpl)
    db.commit()
    db.refresh(db_tpl)
    return db_tpl

@router.put("/{template_id}", response_model=SupervisionTemplateResponse)
def update_template(
    template_id: int,
    tpl: SupervisionTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_tpl = db.query(SupervisionTemplate).filter(SupervisionTemplate.id == template_id).first()
    if not db_tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    for key, value in tpl.model_dump(exclude_unset=True).items():
        setattr(db_tpl, key, value)
    db.commit()
    db.refresh(db_tpl)
    return db_tpl

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    tpl = db.query(SupervisionTemplate).filter(SupervisionTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.query(SupervisionTemplateItem).filter(SupervisionTemplateItem.template_id == template_id).delete()
    db.delete(tpl)
    db.commit()
    return {"message": "删除成功"}

# === Template Items ===

@router.get("/{template_id}/items", response_model=List[SupervisionTemplateItemResponse])
def list_template_items(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tpl = db.query(SupervisionTemplate).filter(SupervisionTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return db.query(SupervisionTemplateItem).filter(
        SupervisionTemplateItem.template_id == template_id
    ).order_by(SupervisionTemplateItem.sort_order).all()

@router.post("/{template_id}/items", response_model=SupervisionTemplateItemResponse)
def create_template_item(
    template_id: int,
    item: SupervisionTemplateItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    tpl = db.query(SupervisionTemplate).filter(SupervisionTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    db_item = SupervisionTemplateItem(template_id=template_id, **item.model_dump(exclude={"template_id"}))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{template_id}/items/{item_id}", response_model=SupervisionTemplateItemResponse)
def update_template_item(
    template_id: int,
    item_id: int,
    item: SupervisionTemplateItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_item = db.query(SupervisionTemplateItem).filter(
        SupervisionTemplateItem.id == item_id,
        SupervisionTemplateItem.template_id == template_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="模板项目不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{template_id}/items/{item_id}")
def delete_template_item(
    template_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    db_item = db.query(SupervisionTemplateItem).filter(
        SupervisionTemplateItem.id == item_id,
        SupervisionTemplateItem.template_id == template_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="模板项目不存在")
    db.delete(db_item)
    db.commit()
    return {"message": "删除成功"}
