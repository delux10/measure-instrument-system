from app.services.base import BaseCRUDService
from app.models.borrow import BorrowRecord, BorrowStatus
from sqlalchemy.orm import Session


class BorrowService(BaseCRUDService):
    def __init__(self):
        super().__init__(BorrowRecord, "借用记录")

    def return_instrument(self, db: Session, id: int, return_date=None):
        from datetime import date
        obj = self.get(db, id)
        obj.status = BorrowStatus.RETURNED
        obj.actual_return_date = return_date or date.today()
        db.commit()
        db.refresh(obj)
        return obj
