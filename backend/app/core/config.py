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
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "edunexus_password"
    POSTGRES_DB: str = "edunexus"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

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