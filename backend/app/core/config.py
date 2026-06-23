"""
应用配置管理 - 从环境变量读取所有配置
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
import json
import os


class Settings(BaseSettings):
    # 应用基础配置
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-this-secret-key-in-production"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://zjfl_user:password@localhost:5432/zjfl_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # JWT 配置
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 邮件配置
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "智链解纷"
    SMTP_TLS: bool = True

    # 短信配置
    ALIYUN_SMS_ACCESS_KEY_ID: str = ""
    ALIYUN_SMS_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = "智链解纷"
    ALIYUN_SMS_TEMPLATE_CODE: str = ""

    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local | oss
    STORAGE_LOCAL_PATH: str = "/app/uploads"
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET_NAME: str = ""
    OSS_ENDPOINT: str = ""
    OSS_REGION: str = ""

    # Agora 视频会议
    AGORA_APP_ID: str = ""
    AGORA_APP_CERTIFICATE: str = ""
    AGORA_ENABLE_MOCK: bool = True

    # 存证服务
    TIMESTAMP_SERVICE_PROVIDER: str = "mock"
    TIMESTAMP_API_URL: str = ""
    TIMESTAMP_API_KEY: str = ""

    # 电子签章
    ESIGN_PROVIDER: str = "mock"
    ESIGN_API_URL: str = ""
    ESIGN_APP_ID: str = ""
    ESIGN_APP_SECRET: str = ""

    # 演示模式
    DEMO_MODE: bool = True

    # 前端配置
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # AES 加密密钥 (32字节)
    AES_KEY: str = "aes-key-32-chars-change-in-prod!!"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # 文件上传限制
    MAX_FILE_SIZE_MB: int = 50
    MAX_BATCH_UPLOAD: int = 10

    # 管理员默认账号
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@zjfl.com"
    ADMIN_PASSWORD: str = "admin123"

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
