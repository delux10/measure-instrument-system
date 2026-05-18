"""应用入口 — 全量重构 v2.0"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, instruments, calibration, contracts, supervision, admin

app = FastAPI(title=settings.APP_NAME, version="2.0.0")

@app.on_event("startup")
def on_startup():
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(admin.router, prefix="/api/admin", tags=["系统管理"])
app.include_router(instruments.router, prefix="/api/instruments", tags=["仪器台账"])
app.include_router(calibration.router, prefix="/api/calibration", tags=["检定管理"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["合同管理"])
app.include_router(supervision.router, prefix="/api/supervision", tags=["监督管理"])
