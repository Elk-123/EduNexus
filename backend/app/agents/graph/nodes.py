"""
LangGraph Agent 节点函数 — 使用工厂模式消除 7 个 Agent 的重复代码

核心设计:
  - _make_agent_node() 工厂函数封装通用执行逻辑:
      构建 Prompt → 调用 LLM → 结构化输出/解析 JSON → 校验 → Fallback
  - 每个 Agent 只需一行定义，7 个 Agent 从 ~120行/个 → ~3行/个
  - 所有节点保持与 v2.0 相同的 Prompt 和输出格式，确保向后兼容

v2.0 旧代码路径仍保留在各 implementations/ 中（标记 [v2.0 legacy]），
本模块提供新的 LangGraph 执行路径，由 pipeline.py 调用。
"""
import json
import logging
from datetime import datetime
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from ..types import AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..prompts.templates import PROMPTS
from ..fallback_data import get_fallback_content
from .state import PipelineState

logger = logging.getLogger("edunexus.agents")


def _make_agent_node(agent_id: str, result_type: str):
    """
    工厂函数: 为每个 Agent 创建 LangGraph Node 函数。

    Args:
        agent_id: Agent 标识 (如 "professor")
        result_type: 输出类型标签 (如 "academic_content")

    Returns:
        callable: async def node(state: PipelineState) → dict (部分 state 更新)

    封装逻辑:
      1. 从 PROMPTS 获取该 Agent 的 Prompt 模板
      2. 调用 LangChainUtils 执行 LLM 调用
      3. 尝试 JSON 解析（先用 try_parse_json，预留 with_structured_output）
      4. 根据 Agent 特有校验规则验证输出
      5. 校验失败或 LLM 异常时，降级到 fallback_data
      6. 返回部分 state 更新 dict

    [建议] Phase 1 升级: 当 schemas/ 中的 Pydantic 模型启用后，
           将 try_parse_json 替换为 with_structured_output()，
           同时删除各 Agent 的手动校验逻辑。
    """
    # ── 各 Agent 的输出校验规则 ──
    # [建议] 这些校验逻辑将在切换到 with_structured_output 后移除，
    #        Pydantic 会自动完成类型校验。
    validators = {
        "manager": lambda parsed: (
            isinstance(parsed.get("tasks"), list)
            and len(parsed["tasks"]) >= 5
        ),
        "professor": lambda parsed: (
            isinstance(parsed.get("title"), str)
            and isinstance(parsed.get("sections"), list)
            and len(parsed["sections"]) > 0
        ),
        "architect": lambda parsed: (
            ("mindmap" in parsed and isinstance(parsed["mindmap"], dict)
             and isinstance(parsed["mindmap"].get("root"), str)
             and isinstance(parsed["mindmap"].get("children"), list))
            or ("root" in parsed and isinstance(parsed.get("children"), list))
        ),
        "examiner": lambda parsed: (
            isinstance(parsed.get("questions"), list)
            and len(parsed["questions"]) > 0
        ),
        "director": lambda parsed: (
            isinstance(parsed.get("scenes"), list)
            and len(parsed["scenes"]) > 0
        ),
        "hacker": lambda parsed: (
            isinstance(parsed.get("code"), str)
            and len(parsed["code"]) > 50
        ),
        "reviewer": lambda parsed: (
            isinstance(parsed.get("suggestions"), list)
            and len(parsed["suggestions"]) > 0
        ),
    }

    async def agent_node(state: PipelineState) -> dict:
        """
        LangGraph Node 函数 — 执行单个 Agent 的 LLM 调用并返回状态更新。
        """
        topic = state["topic"]
        agent_outputs = state.get("agent_outputs", {})
        errors = state.get("error_count", 0)
        start_time = datetime.now()

        try:
            # ── 1. 获取 Prompt ──
            prompt_template_str = PROMPTS.get(agent_id, "")
            if not prompt_template_str:
                raise ValueError(f"No prompt template for agent: {agent_id}")

            # ── 2. 构建 LLM 调用 ──
            prompt_template = LangChainUtils.create_prompt_template(prompt_template_str)

            # 准备输入变量
            inputs = {"topic": topic}
            if agent_id == "reviewer":
                # Reviewer 需要所有上游内容的完整 JSON
                inputs["content"] = json.dumps(agent_outputs, ensure_ascii=False, indent=2)
            else:
                inputs["context"] = json.dumps(agent_outputs, ensure_ascii=False, indent=2)

            # ── 3. 调用 LLM ──
            llm_response = LangChainUtils.execute_chain(prompt_template, inputs)
            parsed = LangChainUtils.try_parse_json(llm_response)

            # ── 4. 校验输出 ──
            validator = validators.get(agent_id)
            if parsed is not None and validator and validator(parsed):
                # ── 5a. Agent 特有后处理 ──
                content = _post_process(agent_id, parsed, topic, agent_outputs)
            else:
                logger.warning(
                    "[Graph] %s: output validation failed, using fallback", agent_id
                )
                content = get_fallback_content(agent_id, topic)

            # ── 6. 构建结果 ──
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            new_outputs = {**agent_outputs, agent_id: content}

            result_entry = {
                "agent_id": agent_id,
                "status": AgentStatus.SUCCESS.value,
                "result": {
                    "content": content,
                    "type": result_type,
                    "timestamp": datetime.now().isoformat(),
                    "log": [f"LangGraph node: {agent_id} completed"],
                },
                "duration": duration,
            }

            logger.info(
                "[Graph] %s completed in %dms", agent_id, duration
            )

            # ── 7. 返回部分 state 更新 ──
            return {
                "agent_outputs": new_outputs,
                "current_agent": agent_id,
                "results": state.get("results", []) + [result_entry],
                "error_count": errors,
            }

        except Exception as error:
            logger.warning(
                "[Graph] %s LLM call failed: %s — using fallback", agent_id, error
            )
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content(agent_id, topic)
            new_outputs = {**agent_outputs, agent_id: fallback_content}

            result_entry = {
                "agent_id": agent_id,
                "status": AgentStatus.SUCCESS.value,
                "result": {
                    "content": fallback_content,
                    "type": result_type,
                    "timestamp": datetime.now().isoformat(),
                    "log": [f"LangGraph node (fallback): {agent_id}"],
                },
                "duration": duration,
            }

            return {
                "agent_outputs": new_outputs,
                "current_agent": agent_id,
                "results": state.get("results", []) + [result_entry],
                "error_count": errors + 1,
            }

    return agent_node


def _post_process(agent_id: str, parsed: dict, topic: str, agent_outputs: dict) -> dict:
    """
    Agent 特有后处理逻辑 — 相当于原 implementations 中各 execute() 的校验+规范化部分。

    [建议] 切换到 with_structured_output() 后，这些后处理大部分可以删除，
           因为 Pydantic 已经在解析时完成了类型转换和默认值填充。
    """
    if agent_id == "manager":
        return {
            "tasks": parsed.get("tasks", []),
            "priority": parsed.get(
                "priority",
                ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
            ),
            "coordination_notes": parsed.get("coordination_notes", []),
        }

    elif agent_id == "professor":
        # topic 关键词校验
        title_ok = any(
            kw in parsed.get("title", "") for kw in topic.split() if len(kw) >= 2
        )
        if not title_ok:
            logger.warning("ProfessorNode: title doesn't contain topic keywords, using fallback")
            return get_fallback_content("professor", topic)
        return {
            "title": parsed["title"],
            "sections": parsed["sections"],
        }

    elif agent_id == "architect":
        if "mindmap" in parsed and isinstance(parsed["mindmap"], dict):
            return parsed
        elif "root" in parsed:
            # v2 旧格式: {root, children} → 包裹为 {mindmap: {root, children}}
            return {"mindmap": parsed}
        return get_fallback_content("architect", topic)

    elif agent_id == "examiner":
        questions = parsed["questions"]
        for q in questions:
            ans = q.get("answer", 0)
            if isinstance(ans, str):
                ans_map = {"a": 0, "A": 0, "b": 1, "B": 1, "c": 2, "C": 2, "d": 3, "D": 3}
                q["answer"] = ans_map.get(ans.strip(), 0)
            elif isinstance(ans, int):
                q["answer"] = ans
            else:
                q["answer"] = 0
            if "explanation" not in q:
                q["explanation"] = "该选项是正确答案。"
        return {"questions": questions}

    elif agent_id == "director":
        scenes = parsed["scenes"]
        # topic 关键词校验
        has_topic = any(
            any(kw in s.get("title", "") for kw in topic.split() if len(kw) >= 2)
            for s in scenes
        )
        if not has_topic:
            logger.warning("DirectorNode: scene titles don't contain topic keywords, using fallback")
            return get_fallback_content("director", topic)

        # 规范化字段
        for i, s in enumerate(scenes):
            s.setdefault("scene_number", i + 1)
            s.setdefault("duration_seconds", 45)
            # 校验 resources
            resources = s.get("resources", [])
            if not isinstance(resources, list) or len(resources) == 0:
                logger.warning("DirectorNode: scene %d missing resources, using fallback", s["scene_number"])
                return get_fallback_content("director", topic)

            valid_resources = []
            for r in resources:
                url = r.get("url", "")
                if _is_valid_video_url(url):
                    r.setdefault("type", "video")
                    r.setdefault("platform", "YouTube")
                    valid_resources.append(r)
                else:
                    logger.warning("DirectorNode: invalid resource url: %s, skipping", url)
            if not valid_resources:
                logger.warning("DirectorNode: scene %d has no valid resources after filtering, using fallback", s["scene_number"])
                return get_fallback_content("director", topic)
            s["resources"] = valid_resources
        return {"scenes": scenes}

    elif agent_id == "hacker":
        exercises = parsed.get("exercises", [])
        normalized_exercises = []
        for ex in exercises:
            if isinstance(ex, str):
                normalized_exercises.append(ex)
            elif isinstance(ex, dict):
                parts = []
                if ex.get("title"):
                    parts.append(ex["title"])
                if ex.get("description"):
                    parts.append(ex["description"])
                if ex.get("requirement"):
                    parts.append(f"要求: {ex['requirement']}")
                normalized_exercises.append(" — ".join(parts) if parts else str(ex))
            else:
                normalized_exercises.append(str(ex))

        return {
            "title": parsed["title"],
            "description": parsed.get("description", ""),
            "code": parsed["code"],
            "expected_output": parsed.get("expected_output", ""),
            "exercises": normalized_exercises
            if normalized_exercises
            else [
                f"修改代码中的参数，观察{topic}的行为变化",
                f"尝试用另一种方法实现{topic}的相同功能",
            ],
        }

    elif agent_id == "reviewer":
        suggestions = parsed.get("suggestions", [])
        qs = parsed.get("quality_score", 85)
        try:
            quality_score = int(float(qs))
        except (ValueError, TypeError):
            quality_score = 85

        return {
            "hallucination_risk": parsed.get("hallucination_risk", "low"),
            "quality_score": quality_score,
            "suggestions": suggestions,
            "difficulty_assessment": parsed.get("difficulty_assessment", "中等"),
        }

    # fallback
    return parsed


def _is_valid_video_url(url: str) -> bool:
    """
    校验视频 URL 是否有效（从 DirectorAgent 迁移过来）。

    拒绝: 搜索链接、假域名、无效视频 ID
    接受: youtube.com/watch?v= 和 youtu.be/ 格式
    """
    import re

    if not url or not isinstance(url, str):
        return False
    url_lower = url.lower().strip()
    if "/results" in url_lower or "search_query" in url_lower:
        return False
    if "example.com" in url_lower:
        return False
    watch_match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', url_lower)
    if watch_match:
        video_id = watch_match.group(1)
        if video_id in ("0", "example", "test", "xxx"):
            return False
        return True
    short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url_lower)
    if short_match:
        video_id = short_match.group(1)
        if video_id in ("0", "example", "test", "xxx"):
            return False
        return True
    return False


# ═══════════════════════════════════════════════════════════════
#  7 个 Agent Node — 一行定义
# ═══════════════════════════════════════════════════════════════

manager_node   = _make_agent_node("manager",   "task_plan")
professor_node = _make_agent_node("professor", "academic_content")
architect_node = _make_agent_node("architect", "mindmap")
examiner_node  = _make_agent_node("examiner",  "quiz")
director_node  = _make_agent_node("director",  "video_script")
hacker_node    = _make_agent_node("hacker",    "code")
reviewer_node  = _make_agent_node("reviewer",  "review")

# Node 映射表
NODES = {
    "manager":   manager_node,
    "professor": professor_node,
    "architect": architect_node,
    "examiner":  examiner_node,
    "director":  director_node,
    "hacker":    hacker_node,
    "reviewer":  reviewer_node,
}
