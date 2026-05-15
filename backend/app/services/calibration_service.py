from app.services.base import BaseCRUDService
from app.models.calibration import CalibrationAgency, CalibrationRecord, Certificate, CalResult
from app.models.instrument import Instrument, InstrumentStatus
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
import hashlib
import shutil


class CalibrationAgencyService(BaseCRUDService):
    def __init__(self):
        super().__init__(CalibrationAgency, "检测院")


class CalibrationRecordService(BaseCRUDService):
    def __init__(self):
        super().__init__(CalibrationRecord, "检定记录")

    def create(self, db: Session, schema):
        obj = self.model(**schema.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        # 更新关联仪器的检定日期
        if schema.actual_date and obj.instrument_id:
            inst = db.query(Instrument).filter(Instrument.id == obj.instrument_id).first()
            if inst:
                inst.last_cal_date = schema.actual_date
                if inst.calibration_cycle:
                    from datetime import timedelta
                    inst.next_cal_date = schema.actual_date + timedelta(days=inst.calibration_cycle * 30)
                if schema.result == CalResult.FAIL:
                    inst.status = InstrumentStatus.STOPPED
                else:
                    inst.status = InstrumentStatus.IN_USE
                db.commit()
        return obj


class CertificateService(BaseCRUDService):
    def __init__(self):
        super().__init__(Certificate, "证书")

    def upload(self, db: Session, calibration_record_id: int, file, upload_dir: str,
               file_type: str = None, valid_from=None, valid_until=None, uploader_name: str = ""):
        os.makedirs(upload_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        safe_name = f"{calibration_record_id}_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, safe_name)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        obj = Certificate(
            calibration_record_id=calibration_record_id,
            file_path=file_path,
            file_type=file_type or file_ext,
            valid_from=valid_from,
            valid_until=valid_until,
            uploader=uploader_name,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id: int):
        obj = self.get(db, id)
        if obj.file_path and os.path.exists(obj.file_path):
            os.remove(obj.file_path)
        db.delete(obj)
        db.commit()
