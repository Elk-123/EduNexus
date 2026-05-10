from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 v1 路由聚合器（含 auth, profile, factory, graph, resources）
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy"}