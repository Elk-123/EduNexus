# backend/app/seed.py
import asyncio
from app.core.database import engine, Base
from app.models.student import Student
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def init_db():
    async with engine.begin() as conn:
        # 强制创建所有表（开发环境测试用）
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 创建一个测试用户
        test_user = Student(
            email="test@edunexus.com",
            username="TestUser",
            hashed_password=get_password_hash("123456"), # 密码为 123456
            onboarding_completed=False
        )
        session.add(test_user)
        await session.commit()
    print("✅ 数据库表已创建，测试账号: test@edunexus.com / 密码: 123456")

if __name__ == "__main__":
    asyncio.run(init_db())# backend/app/seed.py
import asyncio
from app.core.database import engine, Base
from app.models.student import Student
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def init_db():
    async with engine.begin() as conn:
        # 强制创建所有表（开发环境测试用）
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 创建一个测试用户
        test_user = Student(
            email="test@edunexus.com",
            username="TestUser",
            hashed_password=get_password_hash("123456"), # 密码为 123456
            onboarding_completed=False
        )
        session.add(test_user)
        await session.commit()
    print("✅ 数据库表已创建，测试账号: test@edunexus.com / 密码: 123456")

if __name__ == "__main__":
    asyncio.run(init_db())