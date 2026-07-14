import json
import logging
import re
from datetime import datetime
from typing import List, Optional

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.student import Student
from app.schemas.tutor import (
    ChatRequest, ChatResponse, Message,
    ConversationHistory, SolveRequest, SolveResponse, SolveStep,
)
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("edunexus")


# ═══════════════════════════════════════════════════════════════
# System Prompts
# ═══════════════════════════════════════════════════════════════

TUTOR_SYSTEM_PROMPT = """你是一位专业、耐心、鼓励性的 AI 导师，名叫 EduNexus Tutor。你的目标是帮助学生深入理解知识，而不是简单地给出答案。

## 你的教学风格
1. **深入浅出**：用简单的例子和类比解释复杂概念
2. **鼓励性**：肯定学生的努力，给予正向反馈
3. **个性化**：根据学生的背景和水平调整讲解深度
4. **结构化**：回答要有条理，分点说明，便于理解

## 回答格式
- 对于概念性问题：先给出简洁的定义，再用例子说明，最后引导深入思考
- 对于练习题：先最给出完整解析，再提供标准答案
- 对于学习方法类问题：给出具体、可操作的建议

## 限制
- 使用中文回答
- 如果问题超出教育范围，友好地引导学生回到学习主题"""


SOLVE_SYSTEM_PROMPT = """你是一位专业的 AI 解题导师（EduNexus Solver）。你的任务是仔细分析用户上传的题目图片，给出**结构化、逐步**的详细解答。

## 输出要求

你必须严格按照以下 JSON 格式输出，**不要包含任何 markdown 代码块标记**（不要 ```json ```），直接输出纯 JSON：

{
  "steps": [
    {
      "title": "Step 1：审题与分析",
      "content": [
        "提取题目中的关键信息：...",
        "明确题目要求：...",
        "确定解题方向：..."
      ]
    },
    {
      "title": "Step 2：核心推导 / 计算过程",
      "content": [
        "第一步：...",
        "第二步：...",
        "..."
      ]
    },
    {
      "title": "Step 3：验证与结论",
      "content": [
        "验证：...",
        "最终答案：..."
      ]
    }
  ],
  "summary": "一句话总结解题结果"
}

## 规则
1. **每个步骤必须有清晰的标题**，以 "Step N：" 开头
2. **步骤数量**：2~5 个，根据题目复杂度灵活调整
3. **内容以字符串数组给出**，每个元素是一行文本，用于逐行渲染
4. **步骤之间逻辑递进**：审题 → 推导 → 计算 → 验证 → 总结
5. **数学公式**使用 LaTeX 格式：行内用 `$...$`，独立公式用 `$$...$$`
6. **代码**使用 `语言\n...\n` 标记（不用 markdown 围栏）
7. **表格/框图**用 Unicode 字符绘制（┌─┬─┐ 等）
8. **使用中文**回答
9. summary 字段必须简短有力，一句话总结最终答案

## 特别注意
- 如果图片模糊或题目不完整，在第一个 step 中说明并尽力推断
- 如果题目有多种解法，选择最清晰的一种，在 summary 中可提及其他解法思路
- 对于选择题，不仅要给出答案，还要解释每个选项为什么对/错"""


# ═══════════════════════════════════════════════════════════════
# Qwen3-VL-Flash API 调用
# ═══════════════════════════════════════════════════════════════

async def call_qwen(messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """调用 Qwen API (OpenAI 兼容格式)，返回模型原始文本"""
    payload = {
        "model": settings.QWEN_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=120, connect=15, sock_read=90)

    try:
        logger.info(f"Calling Qwen API: model={settings.QWEN_MODEL}, url={settings.QWEN_API_URL}")
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                settings.QWEN_API_URL, json=payload, headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"Qwen response (first 300 chars): {content[:300]}")
                    return content
                else:
                    error_text = await resp.text()
                    logger.error(f"Qwen API error {resp.status}: {error_text[:500]}")
                    raise RuntimeError(f"Qwen API returned {resp.status}: {error_text[:300]}")

    except aiohttp.ClientError as e:
        logger.error(f"Qwen API network error: {e}")
        raise RuntimeError(f"无法连接到 Qwen API：{e}")


async def call_qwen_vision(image_base64: str, prompt: str) -> str:
    """调用 Qwen3-VL-Flash 视觉模型，传入图片和提示词"""
    # 确保 base64 有正确的 data URI 前缀
    if not image_base64.startswith("data:"):
        image_base64 = f"data:image/jpeg;base64,{image_base64}"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_base64},
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]
    return await call_qwen(messages, temperature=0.3, max_tokens=4096)


def parse_solve_json(raw_text: str) -> dict:
    """从 LLM 返回的原始文本中解析出结构化 JSON

    处理多种情况：
    1. 直接是合法 JSON
    2. 包裹在 ```json ... ``` 中
    3. 包裹在 ``` ... ``` 中
    4. 文本中嵌有 JSON 段落
    """
    # 尝试 1: 直接解析
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # 尝试 2: 提取 ```json ... ``` 代码块
    json_block = re.search(r'```json\s*([\s\S]*?)\s*```', raw_text)
    if json_block:
        try:
            return json.loads(json_block.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试 3: 提取 ``` ... ``` 代码块
    code_block = re.search(r'```\s*([\s\S]*?)\s*```', raw_text)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试 4: 查找 { ... } 最外层 JSON
    brace_match = re.search(r'\{[\s\S]*"steps"[\s\S]*"summary"[\s\S]*\}', raw_text)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从 LLM 返回中解析 JSON，原始文本前 500 字符: {raw_text[:5000]}")


# ═══════════════════════════════════════════════════════════════
# API 端点
# ═══════════════════════════════════════════════════════════════

@router.post("/chat", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """向 AI 导师提问（Qwen3-VL-Flash 驱动）"""
    # 构建用户上下文
    user_context = ""
    if current_user.onboarding_completed:
        user_context = f"\n学生姓名: {current_user.username}\n"
    if request.context:
        user_context += f"当前学习上下文: {request.context}\n"

    user_message = f"{user_context}学生问题: {request.message}"

    messages = [
        {"role": "system", "content": TUTOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        reply = await call_qwen(messages, temperature=0.7, max_tokens=2048)
    except Exception as e:
        logger.warning(f"Tutor Qwen call failed, using fallback: {e}")
        reply = generate_fallback_response(request.message)

    return ChatResponse(
        reply=reply,
        message_id=str(datetime.now().timestamp()),
        agent_type="tutor",
        timestamp=datetime.now().isoformat(),
    )


@router.post("/solve", response_model=SolveResponse)
async def solve_problem(
    request: SolveRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """AI 搜题：上传题目图片，获取逐步解答（Qwen3-VL-Flash 视觉模型驱动）

    流程：
    1. 接收 base64 编码的图片
    2. 发送给 Qwen3-VL-Flash 视觉模型
    3. 解析模型返回的结构化 JSON
    4. 返回步骤化解答给前端
    """
    # 构建完整的视觉提示词
    prompt = SOLVE_SYSTEM_PROMPT
    if request.message:
        prompt += f"\n\n用户附加说明：{request.message}"

    logger.info(
        f"Solve request from user={current_user.username}, "
        f"image_size={len(request.image_base64)} chars"
    )

    try:
        raw_response = await call_qwen_vision(request.image_base64, prompt)
        parsed = parse_solve_json(raw_response)

        steps = [
            SolveStep(title=s["title"], content=s["content"])
            for s in parsed.get("steps", [])
        ]
        summary = parsed.get("summary", "解答完成")

        logger.info(f"Solve success: {len(steps)} steps, summary={summary[:80]}")

        return SolveResponse(
            steps=steps,
            summary=summary,
            raw_text=parsed.get("raw_text"),
        )

    except ValueError as e:
        # JSON 解析失败 — 返回原始文本作为兜底
        logger.warning(f"JSON parse failed for solve, returning raw text: {e}")
        raw_response = getattr(e, '__context__', None)
        return SolveResponse(
            steps=[
                SolveStep(
                    title="解答",
                    content=[str(e).split("原始文本")[0].strip() or "解析解答时出现错误，请重试"],
                )
            ],
            summary="解析出错，请重试",
        )
    except Exception as e:
        logger.error(f"Solve failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解题服务暂时不可用：{str(e)[:200]}",
        )


@router.get("/history", response_model=List[ConversationHistory])
async def get_conversation_history(
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Student = Depends(deps.get_current_user),
):
    """获取对话历史（当前返回占位数据，后续接入数据库）"""
    # TODO: 从 tutor_conversations 表查询真实历史
    return []


# ═══════════════════════════════════════════════════════════════
# Fallback（Qwen API 不可用时的兜底）
# ═══════════════════════════════════════════════════════════════

def generate_fallback_response(message: str) -> str:
    """关键词匹配 fallback"""
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
