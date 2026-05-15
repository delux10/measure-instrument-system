from app.services.base import BaseCRUDService
from app.models.supervision import (
    SupervisionTemplate, SupervisionTemplateItem,
    SupervisionPlan, SupervisionExecution, SupervisionCheckItem,
    NonConformity,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException


class SupervisionTemplateService(BaseCRUDService):
    def __init__(self):
        super().__init__(SupervisionTemplate, "监督模板")

    def delete(self, db: Session, id: int):
        obj = self.get(db, id)
        db.query(SupervisionTemplateItem).filter(
            SupervisionTemplateItem.template_id == id
        ).delete()
        db.delete(obj)
        db.commit()


class SupervisionTemplateItemService(BaseCRUDService):
    def __init__(self):
        super().__init__(SupervisionTemplateItem, "监督模板项目")


class SupervisionPlanService(BaseCRUDService):
    def __init__(self):
        super().__init__(SupervisionPlan, "监督计划")


class SupervisionExecutionService(BaseCRUDService):
    def __init__(self):
        super().__init__(SupervisionExecution, "监督执行")

    def delete(self, db, id):
        obj = self.get(db, id)
        db.query(SupervisionCheckItem).filter(
            SupervisionCheckItem.execution_id == id
        ).delete()
        db.delete(obj)
        db.commit()

    def review(self, db, exec_id, reviewer_id, overall_result=None, review_opinion=None, status=None):
        from datetime import date
        obj = self.get(db, exec_id)
        obj.reviewer_id = reviewer_id
        obj.review_date = date.today()
        if overall_result is not None:
            obj.overall_result = overall_result
        if review_opinion is not None:
            obj.review_opinion = review_opinion
        if status is not None:
            obj.status = status
        db.commit()
        db.refresh(obj)
        return obj


class SupervisionCheckItemService(BaseCRUDService):
    def __init__(self):
        super().__init__(SupervisionCheckItem, "监督检查项目")


class NonConformityService(BaseCRUDService):
    def __init__(self):
        super().__init__(NonConformity, "不符合项")

    def create(self, db, schema):
        from datetime import date
        data = schema.model_dump(exclude={"issued_date"})
        existing = db.query(NonConformity).filter(NonConformity.ncr_no == schema.ncr_no).first()
        if existing:
            raise HTTPException(status_code=400, detail="不符合项编号已存在")
        obj = NonConformity(**data)
        obj.issued_date = schema.issued_date or date.today()
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
