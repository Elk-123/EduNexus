import json
import re
import asyncio
import logging
import aiohttp

from app.core.config import settings

logger = logging.getLogger("edunexus")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MAX_RETRIES = 3

SYSTEM_PROMPT = """你是一个专业的教育破冰导师，名叫 EduNexus。你正在与一位新学生进行破冰对话，目标是了解学生的学习背景，以便为其构建个性化的学习画像。

你需要依次了解以下 4 个维度（顺序可灵活调整，自然过渡）：

1. **知识基础** — 学生目前已掌握哪些领域/技能？处于什么水平？
2. **认知风格** — 学生偏好怎样的学习方式？（视觉型、代码实践型、理论推导型、案例教学型等）
3. **学习目标** — 学生的核心学习动力是什么？（考试、求职、兴趣、竞赛等）
4. **时间分布** — 学生的学习时间习惯？（碎片化、沉浸式、周末突击、每日定时等）

## 对话规则
- 每次只问一个问题，语气温暖、专业、鼓励性。
- 每次必须提供 3-6 个可选标签/选项供学生点击选择，以便快速推进对话。
- 学生可以多选选项，也可以输入自由文本补充。
- 你需要在 4-5 轮对话内完成全部 4 个维度的信息收集。
- 当信息足够构建画像时，phase 设为 "summarizing"，用温暖的话语总结学生的情况。

## 输出格式（严格 JSON）
你必须始终以以下 JSON 格式回复，不要输出任何其他内容：

```json
{
  "message": "你的对话消息（一个问题或总结语）",
  "options": ["选项1", "选项2", "选项3", "选项4"],
  "phase": "questioning",
  "collected_data": null
}
```

当 4 个维度都已覆盖，对话可以结束时：
```json
{
  "message": "感谢你分享这些信息...（温暖的总结语）",
  "options": [],
  "phase": "summarizing",
  "collected_data": {
    "knowledge_base": ["已收集的知识点1", "知识点2"],
    "cognitive_style": ["已收集的学习风格"],
    "learning_goals": ["已收集的学习目标"],
    "time_distribution": ["已收集的时间习惯"],
    "notes": ["学生补充的任何自由文本"]
  }
}
```

注意：options 是让用户点击的简短标签（3-8个字），当 phase 为 "summarizing" 时 options 可为空数组。
当 collected_data 不为 null 时，其中每个字段必须是对应维度收集到的所有内容的字符串数组。"""


class OnboardingChatService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL

    async def chat(self, messages: list[dict]) -> dict:
        # 如果是空对话，提供初始问题（fallback）
        if not messages:
            return {
                "message": "你好！我是 EduNexus 的首席破冰导师。很高兴能陪伴你开启这段学习旅程。首先，能告诉我你目前最擅长或已经接触过的领域吗？",
                "options": ["Python 编程", "高等数学", "线性代数", "数据结构", "前端开发", "机器学习基础", "后端架构", "计算机网络"],
                "phase": "questioning",
                "collected_data": None
            }

        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ]

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_read=60)
        connector = aiohttp.TCPConnector(ssl=False)

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Calling DeepSeek API (attempt {attempt + 1}/{MAX_RETRIES})")
                async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                    async with session.post(
                        DEEPSEEK_API_URL, json=payload, headers=headers
                    ) as resp:
                        logger.info(f"DeepSeek API response status: {resp.status}")
                        if resp.status == 200:
                            data = await resp.json()
                            logger.info(f"DeepSeek API response data keys: {data.keys() if isinstance(data, dict) else 'not dict'}")
                            raw_content = data["choices"][0]["message"]["content"].strip()
                            logger.info(f"Raw DeepSeek response (first 500 chars): {raw_content[:500]}")
                            return self._parse_response(raw_content)

                        error_text = await resp.text()
                        logger.error(f"DeepSeek API error {resp.status}: {error_text[:500]}")
                        if resp.status in (429, 503):
                            last_error = RuntimeError(f"DeepSeek 服务繁忙 (attempt {attempt + 1}/{MAX_RETRIES})")
                            logger.warning(f"DeepSeek {resp.status}, retrying in {(attempt + 1) * 2}s")
                            await asyncio.sleep((attempt + 1) * 2)
                            continue
                        raise RuntimeError(f"DeepSeek API error {resp.status}: {error_text}")

            except aiohttp.ClientConnectorError as e:
                last_error = RuntimeError(f"无法连接 DeepSeek API，请检查网络: {str(e)}")
                logger.error(f"ClientConnectorError: {e}")
                raise last_error
            except aiohttp.ClientError as e:
                last_error = RuntimeError(f"DeepSeek 网络请求失败: {str(e)}")
                logger.error(f"ClientError: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep((attempt + 1) * 2)
                    continue
                raise last_error
            except Exception as e:
                last_error = RuntimeError(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected error in DeepSeek chat: {e}", exc_info=True)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep((attempt + 1) * 2)
                    continue
                raise last_error

        # 所有重试失败，返回静态回复
        logger.error("All DeepSeek API attempts failed, falling back to static response")
        return {
            "message": "看来连接有点问题，但我还在。能简单跟我说一下你的学习背景吗？",
            "options": ["Python 编程", "高等数学", "数据结构", "前端开发"],
            "phase": "questioning",
            "collected_data": None
        }

    def _parse_response(self, raw: str) -> dict:
        text = raw.strip()

        # Step 1: Try to extract JSON from markdown code block (```json ... ``` or ``` ... ```)
        code_block_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)```', text)
        if code_block_match:
            json_str = code_block_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning(f"Found code block but failed to parse inner JSON: {json_str[:200]}")
                # Fall through to try the whole text

        # Step 2: Try to find a JSON object anywhere in the text (starts with { and ends with })
        brace_start = text.find('{')
        brace_end = text.rfind('}')
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            json_str = text[brace_start:brace_end + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning(f"Found JSON-like content but parse failed: {json_str[:200]}")

        # Step 3: Direct parse attempt
        if text.startswith("{"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # Step 4: Legacy handling - strip surrounding ``` if text starts with them
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        logger.error(f"Failed to parse DeepSeek response as JSON: {raw[:300]}")
        # 解析失败时：提取原始文本作为消息内容，保持 questioning 阶段继续对话
        # 不要返回 summarizing，否则前端会错误地跳转到总结阶段
        clean_text = raw.strip()
        # 移除 markdown 代码块标记残余
        clean_text = re.sub(r'```(?:json)?', '', clean_text).strip()
        if clean_text:
            return {
                "message": clean_text,
                "options": ["好的，继续", "请再问一个方面", "我补充一点", "换个角度说"],
                "phase": "questioning",
                "collected_data": None
            }
        # 完全为空时的终极兜底
        return {
            "message": "我理解了。能再跟我多说说你的学习情况吗？",
            "options": ["好的，继续", "请再问一个方面", "我补充一点"],
            "phase": "questioning",
            "collected_data": None
        }


onboarding_chat_service = OnboardingChatService()