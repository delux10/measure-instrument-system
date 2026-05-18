"""合同管理 + 对账路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CalibrationContract, ContractItem, ExecutionRecord, ReconciliationDiff, User
from app.schemas import ContractCreate, ContractItemCreate, ExecutionRecordCreate
from app.utils.auth import get_current_user, require_role, apply_department_filter
from app.utils.audit import log

router = APIRouter()

# ── 合同列表 ──
@router.get("/")
def list_contracts(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                   year: int = Query(None), db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    query = apply_department_filter(db.query(CalibrationContract), CalibrationContract, current_user)
    if year: query = query.filter(CalibrationContract.year == year)
    total = query.count()
    items = query.order_by(CalibrationContract.year.desc()).offset((page - 1) * page_size).limit(page_size).all()
    def fmt(c):
        return {"id": c.id, "agency_id": c.agency_id, "year": c.year, "contract_no": c.contract_no,
                "total_amount": c.total_amount, "fields": c.fields or {},
                "agency_name": c.agency.name if c.agency else None,
                "items_count": len(c.items) if c.items else 0}
    return {"data": [fmt(c) for c in items], "meta": {"total": total, "page": page, "page_size": page_size}}

# ── 合同详情 ──
@router.get("/{contract_id}")
def get_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not c: raise HTTPException(404, detail="合同不存在")
    return {"data": {"id": c.id, "agency_id": c.agency_id, "year": c.year, "contract_no": c.contract_no,
                     "total_amount": c.total_amount, "fields": c.fields or {},
                     "agency_name": c.agency.name if c.agency else None,
                     "items": [{"id": i.id, "instrument_name": i.instrument_name, "quantity": i.quantity,
                                "unit_price": i.unit_price, "amount": i.amount, "department_id": i.department_id,
                                "fields": i.fields or {}} for i in (c.items or [])]}}

# ── 创建合同 ──
@router.post("/")
def create_contract(body: ContractCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(require_role(["admin", "system_manager"]))):
    c = CalibrationContract(**body.model_dump())
    db.add(c); db.flush()
    log(db, current_user.id, "create", "contract", c.id, summary=f"新增合同 {c.contract_no}")
    db.commit(); db.refresh(c)
    return {"data": {"id": c.id}}

# ── 合同明细 ──
@router.post("/{contract_id}/items")
def add_item(contract_id: int, body: ContractItemCreate, db: Session = Depends(get_db),
             current_user: User = Depends(require_role(["admin", "system_manager"]))):
    c = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not c: raise HTTPException(404, detail="合同不存在")
    item = ContractItem(contract_id=contract_id, **body.model_dump())
    db.add(item); db.flush()
    log(db, current_user.id, "create", "contract_item", item.id, summary=f"新增合同明细 {body.instrument_name}")
    db.commit()
    return {"data": {"id": item.id}}

# ── 删除合同明细 ──
@router.delete("/{contract_id}/items/{item_id}")
def delete_item(contract_id: int, item_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(["admin", "system_manager"]))):
    item = db.query(ContractItem).filter(ContractItem.id == item_id, ContractItem.contract_id == contract_id).first()
    if not item: raise HTTPException(404, detail="明细不存在")
    db.delete(item); db.commit()
    return {"data": None}

# ── 执行记录 ──
@router.post("/{contract_id}/items/{item_id}/executions")
def add_execution(contract_id: int, item_id: int, body: ExecutionRecordCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(["admin", "system_manager", "dept_measurer"]))):
    item = db.query(ContractItem).filter(ContractItem.id == item_id, ContractItem.contract_id == contract_id).first()
    if not item: raise HTTPException(404, detail="合同明细不存在")
    exec_rec = ExecutionRecord(contract_item_id=item_id, instrument_id=body.instrument_id,
                                actual_date=body.actual_date, actual_quantity=body.actual_quantity,
                                actual_amount=body.actual_amount, department_id=body.department_id or current_user.department_id,
                                fields=body.fields or {})
    db.add(exec_rec); db.flush()
    # 自动对账
    _reconcile(db, item)
    log(db, current_user.id, "create", "execution", exec_rec.id, summary=f"新增执行记录")
    db.commit()
    return {"data": {"id": exec_rec.id}}

# ── 执行记录列表 ──
@router.get("/{contract_id}/items/{item_id}/executions")
def list_executions(contract_id: int, item_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    execs = db.query(ExecutionRecord).filter(ExecutionRecord.contract_item_id == item_id).all()
    return {"data": [{"id": e.id, "actual_date": str(e.actual_date) if e.actual_date else None,
                      "actual_quantity": e.actual_quantity, "actual_amount": e.actual_amount,
                      "fields": e.fields or {}} for e in execs]}

# ── 对账结果 ──
@router.get("/{contract_id}/reconciliation")
def get_reconciliation(contract_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    c = db.query(CalibrationContract).filter(CalibrationContract.id == contract_id).first()
    if not c: raise HTTPException(404, detail="合同不存在")
    items = db.query(ContractItem).filter(ContractItem.contract_id == contract_id).all()
    diffs = db.query(ReconciliationDiff).join(ContractItem).filter(
        ContractItem.contract_id == contract_id).all()
    summary = {"total_contract_amount": 0.0, "total_actual_amount": 0.0, "diff_amount": 0.0, "diff_count": len(diffs)}
    for item in items:
        summary["total_contract_amount"] += item.amount or 0
    for d in diffs:
        summary["total_actual_amount"] += d.diff_amount or 0
    summary["diff_amount"] = summary["total_contract_amount"] - summary["total_actual_amount"]
    return {"data": {"diffs": [{"id": d.id, "diff_type": d.diff_type, "contract_value": d.contract_value,
                                "actual_value": d.actual_value, "diff_amount": d.diff_amount, "status": d.status}
                               for d in diffs], "summary": summary}}

def _reconcile(db, item: ContractItem):
    """自动比对合同明细与实际执行，生成差异记录"""
    db.query(ReconciliationDiff).filter(ReconciliationDiff.contract_item_id == item.id).delete()
    execs = db.query(ExecutionRecord).filter(ExecutionRecord.contract_item_id == item.id).all()
    actual_qty = sum(e.actual_quantity for e in execs)
    actual_amt = sum(e.actual_amount or 0 for e in execs)
    if actual_qty != item.quantity:
        db.add(ReconciliationDiff(contract_item_id=item.id, diff_type="quantity",
                                  contract_value=str(item.quantity), actual_value=str(actual_qty),
                                  diff_amount=abs((item.amount or 0) - actual_amt)))
    if abs((item.amount or 0) - actual_amt) > 0.01:
        db.add(ReconciliationDiff(contract_item_id=item.id, diff_type="amount",
                                  contract_value=str(item.amount), actual_value=str(actual_amt),
                                  diff_amount=(item.amount or 0) - actual_amt))
    if not execs:
        db.add(ReconciliationDiff(contract_item_id=item.id, diff_type="missing",
                                  contract_value=str(item.quantity), actual_value="0",
                                  diff_amount=item.amount))
