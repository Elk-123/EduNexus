"""
LangGraph Agent 节点函数 — 工厂模式消除重复代码

v2.3: Tool Use (LangChain 内置工具 + BaseCallbackHandler)
  - 工具调用自动通过 BaseCallbackHandler.on_tool_start/end 广播到前端
  - ArxivQueryRun + DuckDuckGoSearchRun (langchain_community)
  - code_executor (subprocess 沙箱)
  - 降级: langchain_community 不可用时自动回退到自实现 @tool

核心调用链: pre-LLM 工具(搜索注入) → structured_output → post-LLM 工具(代码验证)
"""
import json
import logging
import time as time_module
from datetime import datetime
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from ..types import AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..prompts.templates import PROMPTS
from ..fallback_data import get_fallback_content
from .state import PipelineState

# ── 结构化输出 Schema ──
from ..schemas.manager import ManagerOutput
from ..schemas.professor import ProfessorOutput
from ..schemas.architect import ArchitectOutput
from ..schemas.examiner import ExaminerOutput
from ..schemas.director import DirectorOutput
from ..schemas.hacker import HackerOutput
from ..schemas.reviewer import ReviewerOutput

SCHEMAS: dict[str, type[BaseModel]] = {
    "manager": ManagerOutput, "professor": ProfessorOutput,
    "architect": ArchitectOutput, "examiner": ExaminerOutput,
    "director": DirectorOutput, "hacker": HackerOutput,
    "reviewer": ReviewerOutput,
}

# ── 反思闭环 ──
REFLECTION_THRESHOLD = 70  # 低于此分触发重写
MAX_RETRIES = 2

# ── Tool Use 配置 ──
# [已注释] get_academic_search — ArXivQueryRun 与 arxiv v2.x 不兼容，改用 web_search
# from ..tools.academic_search import get_academic_search
from ..tools.web_search import get_web_search
from ..tools.youtube_search import get_youtube_search
from ..tools.code_executor import get_code_executor

AGENT_TOOLS: dict[str, dict] = {
    "professor": {"pre_llm": [get_web_search],   "post_llm": []},
    "architect": {"pre_llm": [get_web_search],   "post_llm": []},
    "director":  {"pre_llm": [get_youtube_search], "post_llm": []},
    "hacker":    {"pre_llm": [],                "post_llm": [get_code_executor]},
    "manager":   {"pre_llm": [], "post_llm": []},
    "examiner":  {"pre_llm": [], "post_llm": []},
    "reviewer":  {"pre_llm": [], "post_llm": []},
}

logger = logging.getLogger("edunexus.agents")


# ═══════════════════════════════════════════════════════════════
#  ToolCallbackHandler — 基于 BaseCallbackHandler 的工具事件广播
#  不再手写 callback("tool_start",...), LangChain 自动触发
# ═══════════════════════════════════════════════════════════════

class ToolCallbackHandler(BaseCallbackHandler):
    """
    LangChain 标准回调: 工具调用时自动触发 on_tool_start/end/error。
    将事件转发到 _agent_event 回调 → WebSocket → 前端展示。
    """

    def __init__(self, agent_id: str, agent_callback):
        super().__init__()
        self.agent_id = agent_id
        self._cb = agent_callback  # (agent_id, event_type, data) -> None

    def on_tool_start(self, serialized: dict, input_str: str, *,
                      run_id: str, parent_run_id=None, **kwargs):
        tool_name = serialized.get("name", "tool")
        logger.info("🔧 [%s] → %s(%s)", self.agent_id, tool_name, str(input_str)[:200])
        if self._cb:
            try:
                self._cb(self.agent_id, "tool_start", {"tool": tool_name, "input": str(input_str)})
            except Exception:
                pass

    def on_tool_end(self, output: str, *, run_id: str, parent_run_id=None, **kwargs):
        # 终端完整输出（每行一行日志）
        for line in str(output).split("\n"):
            logger.info("   │ %s", line[:200])
        if self._cb:
            try:
                self._cb(self.agent_id, "tool_end", {"tool": "tool", "output": str(output), "duration_ms": 0})
            except Exception:
                pass

    def on_tool_error(self, error: BaseException, *, run_id: str, parent_run_id=None, **kwargs):
        logger.warning("   ⚠ tool error: %s", error)
        if self._cb:
            try:
                self._cb(self.agent_id, "tool_error", {"tool": "tool", "error": str(error), "duration_ms": 0})
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
#  工具执行辅助
# ═══════════════════════════════════════════════════════════════

def _resolve_tools(tool_getters: list) -> list:
    """将工具工厂函数列表解析为实际工具实例列表（过滤 None）"""
    tools = []
    for getter in tool_getters:
        try:
            t = getter()
            if t is not None:
                tools.append(t)
        except Exception as e:
            logger.warning("Tool resolution failed for %s: %s", getter.__name__, e)
    return tools


def _execute_pre_llm_tools(agent_id: str, topic: str, agent_callback) -> tuple[str, list]:
    """
    执行 pre-LLM 工具（搜索 → 注入 Prompt）。
    返回 (工具结果文本, 成功执行的工具名称列表)。
    工具事件通过 ToolCallbackHandler 自动广播。
    """
    tools_cfg = AGENT_TOOLS.get(agent_id, {})
    tool_getters = tools_cfg.get("pre_llm", [])
    if not tool_getters:
        return "", []

    tools = _resolve_tools(tool_getters)
    if not tools:
        return "", []

    handler = ToolCallbackHandler(agent_id, agent_callback)
    run_config = RunnableConfig(callbacks=[handler])

    all_results = []
    for tool in tools:
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        t0 = time_module.time()

        try:
            # ★ LangChain 标准调用: tool.invoke(input, config)
            #   回调 on_tool_start/end 自动触发，无需手动调 callback()
            try:
                result = tool.invoke({"query": topic, "max_results": 5}, config=run_config)
            except Exception:
                result = tool.invoke(topic, config=run_config)

            elapsed = time_module.time() - t0
            logger.info("   ← %s: %.1fs", tool_name, elapsed)

            if result:
                all_results.append(f"【{tool_name} 搜索结果】\n{str(result)}")
            else:
                all_results.append(f"【{tool_name}】无结果")

        except Exception as err:
            logger.warning("   ⚠ %s failed: %s", tool_name, err)
            all_results.append(f"【{tool_name}】搜索失败: {err}")

    return "\n\n".join(all_results), [t.name for t in tools]


def _execute_post_llm_tools(agent_id: str, topic: str, content: dict, agent_callback) -> dict:
    """执行 post-LLM 工具（代码验证），工具事件通过 ToolCallbackHandler 自动广播。"""
    tools_cfg = AGENT_TOOLS.get(agent_id, {})
    tool_getters = tools_cfg.get("post_llm", [])
    if not tool_getters:
        return content

    tools = _resolve_tools(tool_getters)
    if not tools:
        return content

    handler = ToolCallbackHandler(agent_id, agent_callback)
    run_config = RunnableConfig(callbacks=[handler])

    for tool in tools:
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)

        if agent_id == "hacker":
            code = content.get("code", "")
            if not code or len(code) < 10:
                continue

            logger.info("🔧 [Hacker] → %s (%d chars)", tool_name, len(code))
            t0 = time_module.time()

            try:
                exec_result = tool.invoke({"code": code, "timeout": 30}, config=run_config)
                elapsed = time_module.time() - t0
                logger.info("   ← code exec: %.1fs", elapsed)

                content["_code_execution"] = {
                    "output": str(exec_result),
                    "status": "error" if "Error" in str(exec_result) or "⛔" in str(exec_result) else "success",
                    "duration_ms": int(elapsed * 1000),
                }
            except Exception as err:
                logger.warning("   ⚠ code exec failed: %s", err)
                content["_code_execution"] = {"output": str(err), "status": "error"}

    return content


def agent_name_display(agent_id: str) -> str:
    names = {"manager": "Manager", "professor": "Professor", "architect": "Architect",
             "examiner": "Examiner", "director": "Director", "hacker": "Hacker", "reviewer": "Reviewer"}
    return names.get(agent_id, agent_id)


# ═══════════════════════════════════════════════════════════════
#  _make_agent_node — Agent Node 工厂
# ═══════════════════════════════════════════════════════════════

def _make_agent_node(agent_id: str, result_type: str):
    validators = {
        "manager": lambda p: isinstance(p.get("tasks"), list) and len(p["tasks"]) >= 5,
        "professor": lambda p: isinstance(p.get("title"), str) and isinstance(p.get("sections"), list) and len(p["sections"]) > 0,
        "architect": lambda p: (("mindmap" in p and isinstance(p["mindmap"], dict) and isinstance(p["mindmap"].get("root"), str) and isinstance(p["mindmap"].get("children"), list)) or ("root" in p and isinstance(p.get("children"), list))),
        "examiner": lambda p: isinstance(p.get("questions"), list) and len(p["questions"]) > 0,
        "director": lambda p: isinstance(p.get("scenes"), list) and len(p["scenes"]) > 0,
        "hacker": lambda p: isinstance(p.get("code"), str) and len(p["code"]) > 50,
        "reviewer": lambda p: isinstance(p.get("suggestions"), list) and len(p["suggestions"]) > 0,
    }

    def agent_node(state: PipelineState) -> dict:
        topic = state["topic"]
        agent_outputs = state.get("agent_outputs", {})
        errors = state.get("error_count", 0)
        start_time = datetime.now()
        callback = state.get("_agent_event")

        if callback:
            try: callback(agent_id, "start", None)
            except Exception: pass

        try:
            # ═══ v2.3: pre-LLM 工具 (搜索注入) ═══
            tool_results, _ = _execute_pre_llm_tools(agent_id, topic, callback)

            # ── 1-2. Prompt + 输入 ──
            prompt_template_str = PROMPTS.get(agent_id, "")
            if not prompt_template_str:
                raise ValueError(f"No prompt template: {agent_id}")
            prompt_template = LangChainUtils.create_prompt_template(prompt_template_str)
            inputs = {"topic": topic}
            if agent_id == "reviewer":
                inputs["content"] = json.dumps(agent_outputs, ensure_ascii=False, indent=2)
            else:
                ctx = json.dumps(agent_outputs, ensure_ascii=False, indent=2)
                if tool_results:
                    ctx += f"\n\n【工具搜索结果（请优先参考以下真实资料）】\n{tool_results}"

                # ═══ v2.4: 反思闭环 — Professor 收到低分反馈时重写 ═══
                if agent_id == "professor":
                    feedback = state.get("reviewer_feedback")
                    retries = state.get("retry_count", 0)
                    if feedback and retries < MAX_RETRIES:
                        logger.info("[Reflect] Professor retry #%d — injecting reviewer feedback", retries)
                        ctx += (
                            f"\n\n【⚠️ 质量审查反馈 — 第{retries}次修改】\n"
                            f"上次评分: {feedback.get('score', 0)}/100\n"
                            f"改进建议:\n" +
                            "\n".join(f"- {s}" for s in feedback.get("suggestions", [])) +
                            f"\n\n请根据以上建议重新生成教学内容，提高质量和深度。"
                        )

                inputs["context"] = ctx

            # ── 3. LLM ──
            content = None
            schema = SCHEMAS.get(agent_id)
            if schema:
                try:
                    chain = LangChainUtils.create_structured_chain(prompt_template, schema)
                    content = chain.invoke(inputs).model_dump()
                except Exception as e:
                    logger.info("[Graph] %s: structured output failed (%s), JSON fallback", agent_id, type(e).__name__)

            if content is None:
                llm_response = LangChainUtils.execute_chain(prompt_template, inputs)
                parsed = LangChainUtils.try_parse_json(llm_response)
                validator = validators.get(agent_id)
                if parsed is not None and validator and validator(parsed):
                    content = _post_process(agent_id, parsed, topic, agent_outputs)
                else:
                    content = get_fallback_content(agent_id, topic)

            # ═══ v2.3: post-LLM 工具 (代码验证) ═══
            content = _execute_post_llm_tools(agent_id, topic, content, callback)

            # ═══ v2.4: 反思闭环 — Reviewer 决策 ───
            extra = {}
            if agent_id == "reviewer":
                score = content.get("quality_score", 85)
                retries = state.get("retry_count", 0)
                if score < REFLECTION_THRESHOLD and retries < MAX_RETRIES:
                    logger.info("[Reflect] score=%d < 70 → 触发重试 #%d", score, retries + 1)
                    extra["reviewer_feedback"] = {
                        "score": score,
                        "suggestions": content.get("suggestions", []),
                        "difficulty_assessment": content.get("difficulty_assessment", ""),
                    }
                    extra["retry_count"] = 1
                else:
                    # 评分达标 → 清除反馈（防止旧反馈残留触发误重试）
                    extra["reviewer_feedback"] = None

            # ── 4. 结果 ──
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            result_entry = {
                "agent_id": agent_id, "status": AgentStatus.SUCCESS.value,
                "result": {"content": content, "type": result_type,
                           "timestamp": datetime.now().isoformat(),
                           "log": [f"LangGraph node: {agent_id} completed"]},
                "duration": duration,
            }
            if callback:
                try: callback(agent_id, "done", {"duration": duration, "status": "success"})
                except Exception: pass

            return {"agent_outputs": {agent_id: content}, "current_agent": agent_id,
                    "results": [result_entry], "error_count": 0, **extra}

        except Exception as error:
            logger.warning("[Graph] %s failed: %s — fallback", agent_id, error)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fb = get_fallback_content(agent_id, topic)
            result_entry = {
                "agent_id": agent_id, "status": AgentStatus.SUCCESS.value,
                "result": {"content": fb, "type": result_type,
                           "timestamp": datetime.now().isoformat(),
                           "log": [f"LangGraph node (fallback): {agent_id}"]},
                "duration": duration,
            }
            if callback:
                try: callback(agent_id, "done", {"duration": duration, "status": "fallback", "error": str(error)})
                except Exception: pass

            return {"agent_outputs": {agent_id: fb}, "current_agent": agent_id,
                    "results": [result_entry], "error_count": 1}

    return agent_node


# ═══════════════════════════════════════════════════════════════
#  _post_process (JSON 降级安全网)
# ═══════════════════════════════════════════════════════════════

def _post_process(agent_id: str, parsed: dict, topic: str, agent_outputs: dict) -> dict:
    if agent_id == "manager":
        return {"tasks": parsed.get("tasks", []),
                "priority": parsed.get("priority", ["professor","architect","examiner","director","hacker","reviewer"]),
                "coordination_notes": parsed.get("coordination_notes", [])}
    elif agent_id == "professor":
        if not any(kw in parsed.get("title","") for kw in topic.split() if len(kw) >= 2):
            return get_fallback_content("professor", topic)
        return {"title": parsed["title"], "sections": parsed["sections"]}
    elif agent_id == "architect":
        if "mindmap" in parsed and isinstance(parsed["mindmap"], dict): return parsed
        elif "root" in parsed: return {"mindmap": parsed}
        return get_fallback_content("architect", topic)
    elif agent_id == "examiner":
        for q in parsed.get("questions", []):
            ans = q.get("answer", 0)
            if isinstance(ans, str):
                q["answer"] = {"a":0,"A":0,"b":1,"B":1,"c":2,"C":2,"d":3,"D":3}.get(ans.strip(), 0)
            q.setdefault("explanation", "该选项是正确答案。")
        return {"questions": parsed["questions"]}
    elif agent_id == "director":
        scenes = parsed.get("scenes", [])
        if not any(any(kw in s.get("title","") for kw in topic.split() if len(kw) >= 2) for s in scenes):
            return get_fallback_content("director", topic)
        for i, s in enumerate(scenes):
            s.setdefault("scene_number", i + 1); s.setdefault("duration_seconds", 45)
            valid = [r for r in s.get("resources",[]) if _is_valid_video_url(r.get("url",""))]
            if not valid: return get_fallback_content("director", topic)
            s["resources"] = valid
        return {"scenes": scenes}
    elif agent_id == "hacker":
        exs = parsed.get("exercises", [])
        norm = [e if isinstance(e,str) else " — ".join(filter(None,[e.get(k,"") for k in ("title","description","requirement")])) or str(e) for e in exs]
        return {"title": parsed["title"], "description": parsed.get("description",""),
                "code": parsed["code"], "expected_output": parsed.get("expected_output",""),
                "exercises": norm or [f"修改参数观察{topic}", f"用另一种方法实现{topic}"]}
    elif agent_id == "reviewer":
        qs = parsed.get("quality_score", 85)
        try: qs = int(float(qs))
        except: qs = 85
        return {"hallucination_risk": parsed.get("hallucination_risk","low"), "quality_score": qs,
                "suggestions": parsed.get("suggestions",[]),
                "difficulty_assessment": parsed.get("difficulty_assessment","中等")}
    return parsed


def _is_valid_video_url(url: str) -> bool:
    import re
    if not url or not isinstance(url, str): return False
    u = url.lower().strip()
    if "/results" in u or "search_query" in u or "example.com" in u: return False
    m = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', u)
    if m: return m.group(1) not in ("0","example","test","xxx")
    m = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', u)
    if m: return m.group(1) not in ("0","example","test","xxx")
    return False


# ═══════════════════════════════════════════════════════════════
#  7 个 Agent Node
# ═══════════════════════════════════════════════════════════════

manager_node   = _make_agent_node("manager",   "task_plan")
professor_node = _make_agent_node("professor", "academic_content")
architect_node = _make_agent_node("architect", "mindmap")
examiner_node  = _make_agent_node("examiner",  "quiz")
director_node  = _make_agent_node("director",  "video_script")
hacker_node    = _make_agent_node("hacker",    "code")
reviewer_node  = _make_agent_node("reviewer",  "review")

NODES = {
    "manager": manager_node, "professor": professor_node,
    "architect": architect_node, "examiner": examiner_node,
    "director": director_node, "hacker": hacker_node,
    "reviewer": reviewer_node,
}


# ═══════════════════════════════════════════════════════════════
#  [v2.2 legacy] 旧代码参考
#  _run_tool() / _execute_pre_llm_tools() / _execute_post_llm_tools()
#  旧版使用手写的 callback("tool_start/end/error") 广播。
#  v2.3 已升级为 BaseCallbackHandler 自动触发，见 ToolCallbackHandler 类。
#  完整旧版代码见 git history: ea8a7c4 (7-22)
# ═══════════════════════════════════════════════════════════════
