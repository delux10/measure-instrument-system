from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.contract import CalibrationContract, ContractStatus
from app.models.user import User
from app.schemas import ContractCreate, ContractUpdate, ContractResponse
from app.utils.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[ContractResponse])
def list_contracts(
    status: Optional[str] = Query(None),
    agency_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CalibrationContract)
    if status:
        query = query.filter(CalibrationContract.status == status)
    if agency_id:
        query = query.filter(CalibrationContract.agency_id == agency_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            CalibrationContract.contract_no.ilike(like) | CalibrationContract.name.ilike(like)
        )
    return query.all()

@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract

@router.post("/", response_model=ContractResponse)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    existing = db.query(CalibrationContract).filter(CalibrationContract.contract_no == contract.contract_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="合同编号已存在")
    db_contract = CalibrationContract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    contract: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_contract = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    for key, value in contract.model_dump(exclude_unset=True).items():
        setattr(db_contract, key, value)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@router.delete("/{contract_id}")
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    contract = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    db.delete(contract)
    db.commit()
    return {"message": "删除成功"}
