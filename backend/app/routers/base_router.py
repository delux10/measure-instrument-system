from typing import Callable, Any
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.base import BaseCRUDService
from app.utils.auth import get_current_user


def make_crud_router(
    service: BaseCRUDService,
    create_schema: type,
    update_schema: type,
    *,
    roles_create: list = None,
    roles_update: list = None,
    roles_delete: list = None,
) -> APIRouter:
    """创建标准 CRUD 路由 (5 端点: GET list, GET detail, POST, PUT, DELETE)

    列表接口返回: { items, total, page, page_size }
    详情接口返回: { data, message }
    """
    router = APIRouter()

    # ---- GET / ----
    @router.get("/")
    def list_items(
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        # 从 query params 提取所有过滤条件
        filters = {
            k: v for k, v in request.query_params.items()
            if k not in ("page", "page_size")
            and hasattr(service.model, k)
        }
        # 转换类型
        for k, v in filters.items():
            col = getattr(service.model, k)
            col_type = col.type.python_type if hasattr(col.type, 'python_type') else str
            try:
                if col_type is int and v.isdigit():
                    filters[k] = int(v)
            except Exception:
                pass

        items, total = service.list(db, page=page, page_size=page_size, **filters)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    # ---- GET /{id} ----
    @router.get("/{id}")
    def get_item(
        id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
    ):
        return {"data": service.get(db, id), "message": "success"}

    # ---- POST / ----
    @router.post("/", status_code=201)
    def create_item(
        body: create_schema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return {"data": service.create(db, body), "message": "created"}

    # ---- PUT /{id} ----
    @router.put("/{id}")
    def update_item(
        id: int,
        body: update_schema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return {"data": service.update(db, id, body), "message": "updated"}

    # ---- DELETE /{id} ----
    @router.delete("/{id}")
    def delete_item(
        id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
    ):
        service.delete(db, id)
        return {"data": {"message": "删除成功"}, "message": "deleted"}

    return router
