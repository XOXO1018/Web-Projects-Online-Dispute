"""
后端 API 路由聚合
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, enterprises, cases, evidence,
    negotiation, mediation, notifications, admin, captcha
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(captcha.router, prefix="/captcha", tags=["验证码"])
router.include_router(users.router, prefix="/users", tags=["用户"])
router.include_router(enterprises.router, prefix="/enterprises", tags=["企业"])
router.include_router(cases.router, prefix="/cases", tags=["案件"])
router.include_router(evidence.router, prefix="/evidence", tags=["证据"])
router.include_router(negotiation.router, prefix="/negotiation", tags=["协商"])
router.include_router(mediation.router, prefix="/mediation", tags=["调解"])
router.include_router(notifications.router, prefix="/notifications", tags=["通知"])
router.include_router(admin.router, prefix="/admin", tags=["管理后台"])
