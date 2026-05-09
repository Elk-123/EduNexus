# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1 import auth, profile  # 确保导入了 profile

api_router = APIRouter()

# 注册认证模块
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 注册画像模块 
# 这样注册后，路径会自动拼接成：/api/v1 + /profile + /onboarding
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])