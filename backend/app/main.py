import os
import certifi
from contextlib import asynccontextmanager
import traceback
from typing import Any
from datetime import datetime

# 设置 SSL 证书路径（修复 Windows 下 httpx/aiohttp 的 SSL 问题）
# 注意：必须强制覆盖，因为可能有残留的无效路径
os.environ['SSL_CERT_FILE'] = certifi.where()

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base

# 确保所有模型被导入，以便 create_all 能发现它们
import app.models.student    # noqa: F401
import app.models.profile    # noqa: F401
import app.models.factory    # noqa: F401
import app.models.graph      # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# 全局异常处理器
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理"""
    error_id = f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"

    # 记录错误日志
    error_info = {
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }

    print(f"🚨 [{error_id}] {error_info}")

    # 根据异常类型返回不同的响应
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    elif isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    elif isinstance(exc, SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "数据库操作失败",
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    elif isinstance(exc, Exception):  # AI related errors are now caught as general exceptions
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "AI 服务暂时不可用，请稍后重试",
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    else:
        # 未处理的异常
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "服务器内部错误",
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    description="EduNexus AI 教育平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置 - 根据环境自动调整
if settings.is_production:
    # 生产环境：更严格的 CORS 设置
    allowed_origins = settings.cors_origins_list
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-Requested-With"]
else:
    # 开发环境：宽松的 CORS 设置
    allowed_origins = ["*"]
    allow_methods = ["*"]
    allow_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    expose_headers=["Content-Range", "X-Total-Count"],
)

# 注册全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)

# 注册 v1 路由聚合器（含 auth, profile, factory, graph, resources, tutor, assessment）
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy"}