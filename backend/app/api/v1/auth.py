from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core import security
from app.models.student import Student
from app.schemas.auth import UserCreate, Token, UserResponse, UserLogin

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(obj_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 检查邮箱是否已存在
    result = await db.execute(select(Student).where(Student.email == obj_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="The user with this email already exists.")
    
    # 创建用户
    db_obj = Student(
        email=obj_in.email,
        username=obj_in.username,
        hashed_password=security.get_password_hash(obj_in.password),
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    
    # 生成 Token
    return {
        "access_token": security.create_access_token(db_obj.id),
        "refresh_token": security.create_refresh_token(db_obj.id),
        "user": db_obj
    }

@router.post("/login", response_model=Token)
async def login(obj_in: UserLogin, db: AsyncSession = Depends(get_db)): # 简化起见复用 UserCreate，实际应为 LoginSchema
    result = await db.execute(select(Student).where(Student.email == obj_in.email))
    user = result.scalars().first()
    
    if not user or not security.verify_password(obj_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "access_token": security.create_access_token(user.id),
        "refresh_token": security.create_refresh_token(user.id),
        "user": user
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    # 验证 refresh token
    user_id = security.verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 生成新的 access token
    # 注意：这里简化处理，实际应用中应该验证用户是否存在
    return {
        "access_token": security.create_access_token(user_id),
        "refresh_token": refresh_token,  # 保持原 refresh token 不变
        "user": {
            "id": user_id,
            "email": "refreshed@example.com",
            "username": "RefreshedUser",
            "onboarding_completed": True,
            "created_at": "2026-05-11T00:00:00"
        }
    }