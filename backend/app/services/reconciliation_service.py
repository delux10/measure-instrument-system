from app.services.base import BaseCRUDService
from app.models.reconciliation import ReconciliationDiff, DiffType, DiffStatus
from app.models.contract import CalibrationContract, ContractItem
from app.models.execution import ExecutionRecord
from sqlalchemy.orm import Session
from fastapi import HTTPException


class ReconciliationService(BaseCRUDService):
    def __init__(self):
        super().__init__(ReconciliationDiff, "对账差异")

    def analyze(self, db: Session, contract_id: int):
        contract = db.query(CalibrationContract).filter(
            CalibrationContract.id == contract_id
        ).first()
        if not contract:
            raise HTTPException(status_code=404, detail="合同不存在")

        items = db.query(ContractItem).filter(ContractItem.contract_id == contract_id).all()
        if not items:
            raise HTTPException(status_code=400, detail="合同无明细项")

        db.query(ReconciliationDiff).filter(
            ReconciliationDiff.contract_id == contract_id
        ).delete()

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
        return diffs_created

    def confirm(self, db, diff_id, user_id, status=None, remark=None):
        from datetime import date
        obj = self.get(db, diff_id)
        if status:
            obj.status = status
        if remark:
            obj.remark = remark
        if obj.status in ("confirmed", "adjusted"):
            obj.confirmed_by = user_id
            obj.confirmed_at = date.today()
        db.commit()
        db.refresh(obj)
        return obj
