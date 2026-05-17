from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.contract import CalibrationContract, ContractItem
from app.models.execution import ExecutionRecord
from app.models.reconciliation import ReconciliationDiff, DiffType, DiffStatus
from app.models.user import User
from app.schemas import ReconciliationDiffResponse, ReconciliationDiffUpdate
from app.utils.auth import get_current_user, require_role, apply_department_filter

router = APIRouter()

@router.get("/diffs", response_model=List[ReconciliationDiffResponse])
def list_diffs(
    contract_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    diff_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ReconciliationDiff)
    if contract_id:
        query = query.filter(ReconciliationDiff.contract_id == contract_id)
    if status:
        query = query.filter(ReconciliationDiff.status == status)
    if diff_type:
        query = query.filter(ReconciliationDiff.diff_type == diff_type)
    query = apply_department_filter(query, ReconciliationDiff, current_user)
    return query.all()

@router.post("/analyze/{contract_id}")
def analyze_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    """自动比对合同 vs 实际执行, 找出差异"""
    contract = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    items = db.query(ContractItem).filter(ContractItem.contract_id == contract_id).all()
    if not items:
        raise HTTPException(status_code=400, detail="合同无明细项")
    
    # 清除该合同的旧差异记录
    db.query(ReconciliationDiff).filter(ReconciliationDiff.contract_id == contract_id).delete()
    
    diffs_created = 0
    for item in items:
        executions = db.query(ExecutionRecord).filter(
            ExecutionRecord.contract_item_id == item.id
        ).all()
        
        if not executions:
            db.add(ReconciliationDiff(
                contract_id=contract_id,
                diff_type=DiffType.QUANTITY,
                contract_value=str(item.quantity or 0),
                actual_value="0",
                diff_value=f"合同有 {item.quantity or 0} 件, 实际执行为 0",
                status=DiffStatus.PENDING,
            ))
            diffs_created += 1
            continue
        
        total_qty = sum(e.actual_quantity or 0 for e in executions)
        total_amount = sum(e.actual_amount or 0 for e in executions)
        
        # 数量差异
        if (item.quantity or 0) != total_qty:
            db.add(ReconciliationDiff(
                contract_id=contract_id,
                execution_record_id=executions[0].id,
                diff_type=DiffType.QUANTITY,
                contract_value=str(item.quantity or 0),
                actual_value=str(total_qty),
                diff_value=f"差异: {abs((item.quantity or 0) - total_qty)}",
                status=DiffStatus.PENDING,
            ))
            diffs_created += 1
        
        # 金额差异
        if (item.amount or 0) != total_amount:
            db.add(ReconciliationDiff(
                contract_id=contract_id,
                execution_record_id=executions[0].id,
                diff_type=DiffType.AMOUNT,
                contract_value=str(item.amount or 0),
                actual_value=str(round(total_amount, 2)),
                diff_value=f"差异: {round(abs((item.amount or 0) - total_amount), 2)}",
                status=DiffStatus.PENDING,
            ))
            diffs_created += 1
    
    db.commit()
    return {
        "message": f"对账完成, 共发现 {diffs_created} 项差异",
        "diffs_count": diffs_created
    }

@router.put("/diffs/{diff_id}")
def update_diff(
    diff_id: int,
    diff_update: ReconciliationDiffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    from datetime import date
    db_diff = db.query(ReconciliationDiff).filter(ReconciliationDiff.id == diff_id).first()
    if not db_diff:
        raise HTTPException(status_code=404, detail="差异记录不存在")
    for key, value in diff_update.model_dump(exclude_unset=True).items():
        setattr(db_diff, key, value)
    if diff_update.status in ("confirmed", "adjusted"):
        db_diff.confirmed_by = current_user.id
        db_diff.confirmed_at = date.today()
    db.commit()
    db.refresh(db_diff)
    return db_diff

@router.get("/diffs/{diff_id}", response_model=ReconciliationDiffResponse)
def get_diff(diff_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    diff = db.query(ReconciliationDiff).filter(ReconciliationDiff.id == diff_id).first()
    if not diff:
        raise HTTPException(status_code=404, detail="差异记录不存在")
    return diff
