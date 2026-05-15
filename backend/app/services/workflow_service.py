from app.services.base import BaseCRUDService
from app.models.workflow import Workflow, WorkflowNode
from sqlalchemy.orm import Session


class WorkflowService(BaseCRUDService):
    def __init__(self):
        super().__init__(Workflow, "审批流")

    def delete(self, db: Session, id: int):
        obj = self.get(db, id)
        db.query(WorkflowNode).filter(WorkflowNode.workflow_id == id).delete()
        db.delete(obj)
        db.commit()


class WorkflowNodeService(BaseCRUDService):
    def __init__(self):
        super().__init__(WorkflowNode, "审批节点")

    def update(self, db, node_id, schema):
        from datetime import date
        obj = self.get(db, node_id)
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        if schema.status in ("approved", "rejected"):
            obj.operated_at = date.today()
        db.commit()
        db.refresh(obj)
        return obj
