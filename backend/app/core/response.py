"""
统一响应格式与错误处理
"""
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Optional


def success(data: Any = None, message: str = "success", code: int = 200) -> dict:
    return {"code": code, "message": message, "data": data}


def error(message: str = "error", code: int = 400, data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}


class AppException(HTTPException):
    def __init__(self, status_code: int = 400, message: str = "请求错误", data: Any = None):
        super().__init__(status_code=status_code, detail={"code": status_code, "message": message, "data": data})


class PermissionDenied(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(status_code=403, message=message)


class NotFound(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(status_code=404, message=message)


class Unauthorized(AppException):
    def __init__(self, message: str = "未授权，请先登录"):
        super().__init__(status_code=401, message=message)
