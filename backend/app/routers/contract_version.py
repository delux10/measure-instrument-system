from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import hashlib
from app.database import get_db
from app.models.contract import ContractVersion
from app.models.user import User
from app.schemas import ContractVersionCreate, ContractVersionResponse
from app.utils.auth import get_current_user, require_role, apply_department_filter
from app.config import settings

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "contracts")

@router.get("/", response_model=List[ContractVersionResponse])
def list_versions(
    contract_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ContractVersion)
    if contract_id:
        query = query.filter(ContractVersion.contract_id == contract_id).order_by(ContractVersion.version_no.desc())
    query = apply_department_filter(query, ContractVersion, current_user)
    return query.all()

@router.get("/{version_id}", response_model=ContractVersionResponse)
def get_version(version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ver = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="合同版本不存在")
    return ver

@router.post("/", response_model=ContractVersionResponse)
async def upload_version(
    contract_id: int = Form(...),
    version_no: str = Form(...),
    version_label: Optional[str] = Form(None),
    file: UploadFile = File(...),
    remark: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE // (1024*1024)}MB)")
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    safe_name = f"contract_{contract_id}_v{version_no}_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(content)
    
    file_size = os.path.getsize(file_path)
    file_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
    
    db_ver = ContractVersion(
        contract_id=contract_id,
        version_no=version_no,
        version_label=version_label,
        file_path=file_path,
        file_size=file_size,
        file_hash=file_hash,
        uploader_id=current_user.id,
        remark=remark
    )
    db.add(db_ver)
    db.commit()
    db.refresh(db_ver)
    return db_ver

@router.post("/{version_id}/set-current")
def set_current_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    ver = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="合同版本不存在")
    db.query(ContractVersion).filter(ContractVersion.contract_id == ver.contract_id).update({"is_current": 0})
    ver.is_current = 1
    db.commit()
    return {"message": "已设为当前版本"}

@router.delete("/{version_id}")
def delete_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    ver = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="合同版本不存在")
    if ver.file_path and os.path.exists(ver.file_path):
        os.remove(ver.file_path)
    db.delete(ver)
    db.commit()
    return {"message": "删除成功"}
