from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth_router, department_router, user_router,
    instrument_router, instrument_category_router,
    calibration_agency_router, calibration_record_router, certificate_router,
    contract_router, contract_item_router, contract_version_router,
    execution_record_router, reconciliation_router,
    supervision_template_router, supervision_plan_router,
    supervision_execution_router, non_conformity_router,
    workflow_router, borrow_router, repair_router
)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="测量仪器仪表全生命周期管理系统 API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs(os.path.join(settings.UPLOAD_DIR, "certificates"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "contracts"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "photos"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "evidence"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "signatures"), exist_ok=True)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Health check
@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION, "service": settings.APP_NAME}

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(department_router, prefix="/api/departments", tags=["部门管理"])
app.include_router(user_router, prefix="/api/users", tags=["用户管理"])
app.include_router(instrument_router, prefix="/api/instruments", tags=["仪器台账"])
app.include_router(instrument_category_router, prefix="/api/instrument-categories", tags=["仪器分类"])
app.include_router(calibration_agency_router, prefix="/api/calibration-agencies", tags=["检测院管理"])
app.include_router(calibration_record_router, prefix="/api/calibration-records", tags=["检定记录"])
app.include_router(certificate_router, prefix="/api/certificates", tags=["证书管理"])
app.include_router(contract_router, prefix="/api/contracts", tags=["合同管理"])
app.include_router(contract_item_router, prefix="/api/contract-items", tags=["合同明细"])
app.include_router(contract_version_router, prefix="/api/contract-versions", tags=["合同版本"])
app.include_router(execution_record_router, prefix="/api/execution-records", tags=["实际执行记录"])
app.include_router(reconciliation_router, prefix="/api/reconciliation", tags=["对账管理"])
app.include_router(supervision_template_router, prefix="/api/supervision-templates", tags=["监督模板"])
app.include_router(supervision_plan_router, prefix="/api/supervision-plans", tags=["监督计划"])
app.include_router(supervision_execution_router, prefix="/api/supervision-executions", tags=["监督执行"])
app.include_router(non_conformity_router, prefix="/api/non-conformities", tags=["不符合项"])
app.include_router(workflow_router, prefix="/api/workflows", tags=["审批流程"])
app.include_router(borrow_router, prefix="/api/borrows", tags=["借用管理"])
app.include_router(repair_router, prefix="/api/repairs", tags=["维修管理"])
