from app.routers.auth import router as auth_router
from app.routers.department import router as department_router
from app.routers.user import router as user_router
from app.routers.instrument import router as instrument_router
from app.routers.instrument_category import router as instrument_category_router
from app.routers.calibration_agency import router as calibration_agency_router
from app.routers.calibration_record import router as calibration_record_router
from app.routers.certificate import router as certificate_router
from app.routers.calibration_contract import router as contract_router
from app.routers.contract_item import router as contract_item_router
from app.routers.contract_version import router as contract_version_router
from app.routers.execution_record import router as execution_record_router
from app.routers.reconciliation import router as reconciliation_router
from app.routers.supervision_template import router as supervision_template_router
from app.routers.supervision_plan import router as supervision_plan_router
from app.routers.supervision_execution import router as supervision_execution_router
from app.routers.non_conformity import router as non_conformity_router
from app.routers.workflow import router as workflow_router
from app.routers.borrow import router as borrow_router
from app.routers.repair import router as repair_router
from app.routers.uploads import router as upload_router

__all__ = [
    "auth_router", "department_router", "user_router",
    "instrument_router", "instrument_category_router",
    "calibration_agency_router", "calibration_record_router", "certificate_router",
    "contract_router", "contract_item_router", "contract_version_router",
    "execution_record_router", "reconciliation_router",
    "supervision_template_router", "supervision_plan_router",
    "supervision_execution_router", "non_conformity_router",
    "workflow_router", "borrow_router", "repair_router", "upload_router"
]
