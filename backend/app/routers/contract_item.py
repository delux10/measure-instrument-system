from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.contract import ContractItem
from app.models.user import User
from app.schemas import ContractItemCreate, ContractItemUpdate, ContractItemResponse
from app.utils.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[ContractItemResponse])
def list_items(
    contract_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ContractItem)
    if contract_id:
        query = query.filter(ContractItem.contract_id == contract_id)
    return query.all()

@router.get("/{item_id}", response_model=ContractItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="合同明细不存在")
    return item

@router.post("/", response_model=ContractItemResponse)
def create_item(
    item: ContractItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_item = ContractItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=ContractItemResponse)
def update_item(
    item_id: int,
    item: ContractItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="合同明细不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="合同明细不存在")
    db.delete(item)
    db.commit()
    return {"message": "删除成功"}
