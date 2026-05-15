from app.services.base import BaseCRUDService
from app.models.repair import RepairRecord


class RepairService(BaseCRUDService):
    def __init__(self):
        super().__init__(RepairRecord, "维修记录")
