import json
import logging
from datetime import datetime
from typing import List, Optional

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.student import Student
from app.schemas.tutor import ChatRequest, ChatResponse, Message, ConversationHistory
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("edunexus")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

TUTOR_SYSTEM_PROMPT = """你是一位专业、耐心、鼓励性的 AI 导师，名叫 EduNexus Tutor。你的目标是帮助学生深入理解知识，而不是简单地给出答案。

## 你的教学风格
1. **苏格拉底式引导**：通过提问引导学生思考，而不是直接给出答案
2. **深入浅出**：用简单的例子和类比解释复杂概念
3. **鼓励性**：肯定学生的努力，给予正向反馈
4. **个性化**：根据学生的背景和水平调整讲解深度
5. **结构化**：回答要有条理，分点说明，便于理解

## 回答格式
- 对于概念性问题：先给出简洁的定义，再用例子说明，最后引导深入思考
- 对于练习题：先引导学生自己尝试，再给出提示，最后才给出完整解答
- 对于学习方法类问题：给出具体、可操作的建议

## 限制
- 回答控制在 500 字以内，除非学生明确要求详细解释
- 使用中文回答
- 如果问题超出教育范围，友好地引导学生回到学习主题"""


@router.post("/chat", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """向 AI 导师提问（DeepSeek 驱动）"""
    reply = await call_deepseek_tutor(request.message, request.context, current_user)

    return ChatResponse(
        reply=reply,
        message_id=str(datetime.now().timestamp()),
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
    # 返回模拟数据，实际应该从数据库查询
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

    return history[:limit]


async def call_deepseek_tutor(message: str, context: Optional[str], user: Student) -> str:
    """调用 DeepSeek API 生成导师回复"""
    # 构建用户上下文
    user_context = ""
    if user.onboarding_completed:
        user_context = f"\n学生姓名: {user.username}\n"
    if context:
        user_context += f"当前学习上下文: {context}\n"

    user_message = f"{user_context}学生问题: {message}"

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": TUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=60, connect=15, sock_read=30)

    try:
        logger.info(f"Calling DeepSeek API for tutor chat")
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                DEEPSEEK_API_URL, json=payload, headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"DeepSeek tutor response (first 200 chars): {reply[:200]}")
                    return reply
                else:
                    error_text = await resp.text()
                    logger.error(f"DeepSeek API error {resp.status}: {error_text[:500]}")
                    raise RuntimeError(f"DeepSeek API returned {resp.status}")

    except Exception as e:
        logger.warning(f"Tutor DeepSeek call failed, using fallback: {e}")
        return generate_fallback_response(message)


def generate_fallback_response(message: str) -> str:
    """DeepSeek 不可用时的关键词匹配 fallback"""
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
