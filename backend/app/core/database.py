# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. 创建异步引擎
# echo=True 会在控制台打印所有 SQL 语句，开发阶段非常有用
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,  # 自动检查连接是否存活
    pool_size=10,        # 连接池基础大小
    max_overflow=20      # 允许临时超出的连接数
)

# 2. 创建异步会话工厂
# expire_on_commit=False 是异步模式的关键，防止提交后访问对象属性触发意外的同步查询
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. 声明式基类（供所有 models 继承）
class Base(DeclarativeBase):
    pass

# 4. 依赖注入函数：供 FastAPI 路由使用
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()