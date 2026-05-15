from app.services.base import BaseCRUDService
from app.models.contract import CalibrationContract, ContractVersion, ContractItem, ContractStatus
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
import hashlib


class CalibrationContractService(BaseCRUDService):
    def __init__(self):
        super().__init__(CalibrationContract, "合同")

    def create(self, db: Session, schema):
        existing = db.query(CalibrationContract).filter(
            CalibrationContract.contract_no == schema.contract_no
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="合同编号已存在")
        return super().create(db, schema)


class ContractVersionService(BaseCRUDService):
    def __init__(self):
        super().__init__(ContractVersion, "合同版本")

    def upload(self, db, contract_id, version_no, file, upload_dir,
               version_label=None, remark=None, uploader_id=None):
        os.makedirs(upload_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        safe_name = f"contract_{contract_id}_v{version_no}_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, safe_name)
        with open(file_path, "wb") as f:
            import shutil
            shutil.copyfileobj(file.file, f)
        file_size = os.path.getsize(file_path)
        file_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
        obj = ContractVersion(
            contract_id=contract_id, version_no=version_no,
            version_label=version_label, file_path=file_path,
            file_size=file_size, file_hash=file_hash,
            uploader_id=uploader_id, remark=remark,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def set_current(self, db, version_id):
        ver = self.get(db, version_id)
        db.query(ContractVersion).filter(
            ContractVersion.contract_id == ver.contract_id
        ).update({"is_current": 0})
        ver.is_current = 1
        db.commit()

    def delete(self, db, id):
        ver = self.get(db, id)
        if ver.file_path and os.path.exists(ver.file_path):
            os.remove(ver.file_path)
        db.delete(ver)
        db.commit()


class ContractItemService(BaseCRUDService):
    def __init__(self):
        super().__init__(ContractItem, "合同明细")
