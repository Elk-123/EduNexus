from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.schemas.profile import OnboardingSubmission, ProfileResponse, ProfileDimensions
from app.models.profile import StudentProfile
from app.services.profile_analyzer import analyzer

router = APIRouter()


@router.post("/onboarding", response_model=ProfileResponse)
async def submit_onboarding(
    payload: OnboardingSubmission,
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    """提交破冰对话数据，调用 AI 分析生成结构化画像，并存入数据库"""
    # 1. 调用 AI 分析引擎
    try:
        structured_profile: ProfileDimensions = await analyzer.analyze_onboarding_data(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 分析画像失败: {str(e)}",
        )

    # 2. 查找或创建画像记录
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    db_profile = result.scalars().first()

    if db_profile:
        db_profile.profile_data = structured_profile.model_dump()
        db_profile.raw_responses = payload.responses
        db_profile.version += 1
    else:
        db_profile = StudentProfile(
            student_id=current_user.id,
            profile_data=structured_profile.model_dump(),
            raw_responses=payload.responses,
            version=1,
        )
        db.add(db_profile)

    # 标记用户已完成 onboarding
    current_user.onboarding_completed = True

    # 提交由 get_db 依赖在函数返回后统一执行，无需手动 commit
    return db_profile


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    """获取当前登录学生的画像数据"""
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    db_profile = result.scalars().first()

    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="尚未创建个人画像，请先完成破冰流程。",
        )

    return db_profile
