from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.student import Student
from app.schemas.tutor import ChatRequest, ChatResponse, Message, ConversationHistory

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """向 AI 导师提问"""
    # 这里先实现一个简单的响应，后续可以集成 Gemini API
    response = generate_ai_response(request.message, current_user)

    # 保存对话记录到数据库（简化实现，实际应该有专门的表）
    return ChatResponse(
        reply=response,
        message_id=str(datetime.now().timestamp()),  # 临时使用时间戳作为 ID
        agent_type="tutor",
        timestamp=datetime.now().isoformat()
    )


@router.get("/history", response_model=List[ConversationHistory])
async def get_conversation_history(
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取对话历史"""
    # 这里返回模拟数据，实际应该从数据库查询
    history = [
        ConversationHistory(
            id="1",
            topic="微积分基础",
            preview="如何理解微积分的基本概念？",
            timestamp="2024-05-11T10:30:00",
            message_count=5,
        ),
        ConversationHistory(
            id="2",
            topic="线性代数矩阵运算",
            preview="矩阵乘法的计算方法...",
            timestamp="2024-05-10T15:20:00",
            message_count=8,
        ),
        ConversationHistory(
            id="3",
            topic="Python 编程技巧",
            preview="如何提高代码效率？",
            timestamp="2024-05-09T09:15:00",
            message_count=12,
        ),
    ]

    # 只返回指定数量的记录
    return history[:limit]


def generate_ai_response(message: str, user: Student) -> str:
    """生成 AI 导师的回复（简化版）"""
    # 根据用户画像定制回复
    user_profile = getattr(user, 'onboarding_completed', False)

    # 简单的关键词匹配
    message_lower = message.lower()

    if any(word in message_lower for word in ['微积分', '导数', '积分']):
        return "微积分是数学的重要分支。理解微积分的关键在于掌握极限的概念。导数表示变化率，积分表示累积量。建议从实际例子开始理解，比如速度与路程的关系。"

    elif any(word in message_lower for word in ['线性代数', '矩阵', '向量']):
        return "线性代数研究向量空间和线性映射。矩阵是线性变换的表示方法。在计算机科学中，线性代数广泛应用于图形学、机器学习等领域。"

    elif any(word in message_lower for word in ['编程', '代码', '程序']):
        return "编程是解决问题的过程。建议：1. 先理解算法逻辑 2. 写伪代码 3. 逐步实现 4. 测试调试 5. 优化改进。多练习是提高的关键。"

    elif any(word in message_lower for word in ['学习', '方法', '效率']):
        return "有效的学习策略包括：制定明确目标、使用间隔重复、主动回忆、实践应用、定期复习。找到适合自己的学习节奏比单纯的学习时间更重要。"

    elif any(word in message_lower for word in ['考试', '准备', '复习']):
        return "考试准备建议：1. 制定复习计划 2. 理解概念而非死记硬背 3. 做练习题 4. 找出自己的薄弱环节 5. 保持良好心态。"

    else:
        return "这是一个很好的问题！让我来帮助您理解。首先，我们需要明确这个概念的基本定义，然后通过具体的例子来加深理解。如果您能提供更多背景信息，我可以给您更针对性的建议。"