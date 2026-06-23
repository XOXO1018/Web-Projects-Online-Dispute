"""
智链解纷 - FastAPI 主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import time
import json

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis_client import redis_client
from app.api.v1 import router as api_v1_router
from app.websocket.handler import router as ws_router
from app.core.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("智链解纷平台启动中...")
    await redis_client.connect()
    logger.info("Redis 连接成功")
    yield
    # 关闭时
    await redis_client.disconnect()
    logger.info("智链解纷平台关闭")


app = FastAPI(
    title="智链解纷 API",
    description="中国-东盟跨境商事纠纷在线解决平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        json.dumps({
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "client_ip": request.client.host if request.client else "unknown",
        })
    )
    return response


# 注册路由
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws")

# 静态文件
import os
os.makedirs("/app/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "zjfl-backend", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )
