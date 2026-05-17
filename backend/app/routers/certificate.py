from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import hashlib
from datetime import date
from app.database import get_db
from app.models.calibration import Certificate
from app.models.user import User
from app.schemas import CertificateCreate, CertificateResponse
from app.utils.auth import get_current_user, require_role
from app.config import settings

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "certificates")

@router.get("/", response_model=List[CertificateResponse])
def list_certificates(
    calibration_record_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Certificate)
    if calibration_record_id:
        query = query.filter(Certificate.calibration_record_id == calibration_record_id)
    return query.all()

@router.get("/{cert_id}", response_model=CertificateResponse)
def get_certificate(cert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="证书不存在")
    return cert

@router.post("/", response_model=CertificateResponse)
async def upload_certificate(
    calibration_record_id: int = Form(...),
    file: UploadFile = File(...),
    file_type: Optional[str] = Form(None),
    valid_from: Optional[date] = Form(None),
    valid_until: Optional[date] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE // (1024*1024)}MB)")
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    safe_name = f"{calibration_record_id}_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(content)
    
    db_cert = Certificate(
        calibration_record_id=calibration_record_id,
        file_path=file_path,
        file_type=file_type or file_ext,
        valid_from=valid_from,
        valid_until=valid_until,
        uploader=current_user.name
    )
    db.add(db_cert)
    db.commit()
    db.refresh(db_cert)
    return db_cert

@router.delete("/{cert_id}")
def delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="证书不存在")
    if cert.file_path and os.path.exists(cert.file_path):
        os.remove(cert.file_path)
    db.delete(cert)
    db.commit()
    return {"message": "删除成功"}
