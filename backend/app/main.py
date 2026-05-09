from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vue 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}