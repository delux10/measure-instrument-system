from app.services.base import BaseCRUDService
from app.models.execution import ExecutionRecord
from app.models.contract import ContractItem
from sqlalchemy.orm import Session


class ExecutionRecordService(BaseCRUDService):
    def __init__(self):
        super().__init__(ExecutionRecord, "执行记录")

    def list(self, db: Session, *, page=1, page_size=20, contract_id=None, **filters):
        query = db.query(self.model)
        if contract_id:
            query = query.join(ExecutionRecord.contract_item).filter(
                ContractItem.contract_id == contract_id
            )
        for attr, value in filters.items():
            if value is not None and hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total
