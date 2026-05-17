import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()

ALLOWED_SUBDIRS = {"certificates", "contracts", "photos", "evidence", "signatures"}


@router.get("/{subdir}/{filename}")
def serve_upload(
    subdir: str,
    filename: str,
    current_user: User = Depends(get_current_user),
):
    if subdir not in ALLOWED_SUBDIRS:
        raise HTTPException(status_code=404, detail="目录不存在")
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="非法文件名")

    file_path = os.path.join(settings.UPLOAD_DIR, subdir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(file_path)
