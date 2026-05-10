# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1 import auth, profile, factory, graph, resources

api_router = APIRouter()

# 注册认证模块
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 注册画像模块
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])

# 注册内容工厂模块（含 WebSocket）
api_router.include_router(factory.router, prefix="/factory", tags=["factory"])

# 注册学习路径模块
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])

# 注册资源推送模块
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])