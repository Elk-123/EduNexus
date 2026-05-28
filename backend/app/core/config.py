# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Any

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNexus"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 环境配置
    ENVIRONMENT: str = "development"  # development, production, testing

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "edunexus_password"
    POSTGRES_DB: str = "edunexus"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # DeepSeek API (用于破冰对话和资源生成)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Demo mode — 演示时跳过真实 LLM 调用，直接返回 fallback 内容
    DEMO_MODE: bool = False

    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        """将 CORS_ORIGINS 字符串转换为列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, values: Any) -> Any:
        # 如果 .env 已经提供了完整的 DATABASE_URL，直接用它
        if isinstance(v, str) and v.startswith("postgresql"):
            return v
        
        data = values.data if hasattr(values, 'data') else values
        return f"postgresql+asyncpg://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_SERVER')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"

    # 强制 Pydantic 查找 .env 的绝对路径
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# --- 添加这行调试代码 ---
print(f"DEBUG: Connecting to DB with URL: {settings.DATABASE_URL}")