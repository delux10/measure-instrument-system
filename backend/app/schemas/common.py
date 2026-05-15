from pydantic import BaseModel
from typing import Optional, List, TypeVar, Generic

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """单条数据响应"""
    data: T
    message: str = "success"


class PaginatedResponse(BaseModel, Generic[T]):
    """分页列表响应"""
    items: List[T]
    total: int
    page: int
    page_size: int
