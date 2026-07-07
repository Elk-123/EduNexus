"""
Markdown 生成工具 — 将 Agent 输出格式化为结构化 Markdown 文档
兼容 v1.0.0 mock 数据格式和 v2.0.0 LLM 直接输出格式
"""
from typing import Dict, Any, List


class MarkdownGeneratorTool:
    """Markdown 格式化器 — 将各 Agent 的 JSON 输出转为可读 Markdown"""

    # ═══════════════════════════════════════════════════════════
    #  学术内容（教授）
    # ═══════════════════════════════════════════════════════════
    def generate_academic_content(self, content: Dict[str, Any]) -> str:
        """格式化教授智能体输出的学术内容
        兼容 v1 格式: {{title, sections: [{{heading, subsections: [{{subheading, body}}]}}]}}
        兼容 v2 旧格式: {{title, sections: [{{heading, body}}]}}
        """
        md = f"# {content.get('title', '教学内容')}\n\n"
        for section in content.get("sections", []):
            heading = section.get("heading", "章节")
            md += f"## {heading}\n\n"

            # v1 格式：subsections
            if section.get("subsections"):
                for sub in section["subsections"]:
                    subheading = sub.get("subheading", "")
                    body = sub.get("body", "")
                    if subheading:
                        md += f"### {subheading}\n\n"
                    md += f"{body}\n\n"
            # v2 旧格式：直接 body
            elif section.get("body"):
                md += f"{section['body']}\n\n"

        # 关键概念
        if content.get("keyConcepts"):
            md += "## 关键概念\n\n"
            for c in content["keyConcepts"]:
                if isinstance(c, dict):
                    md += f"- **{c.get('name', '')}**: {c.get('explanation', '')}\n"
                else:
                    md += f"- {c}\n"
        return md

    # ═══════════════════════════════════════════════════════════
    #  思维导图（架构师）
    # ═══════════════════════════════════════════════════════════
    def generate_mindmap(self, content: Dict[str, Any]) -> str:
        """格式化思维导图
        兼容 v1 格式: {{mindmap: {{root, children}}}}
        兼容 v2 旧格式: {{root, children}}
        """
        # v1 兼容：解包 mindmap 顶层 key
        mindmap = content.get("mindmap", content)
        root = mindmap.get("root", "主题")
        children = mindmap.get("children", [])

        md = f"# 知识结构: {root}\n\n```mermaid\ngraph TD\n"
        md += self._render_mermaid(root, children)
        md += "\n```\n"
        return md

    def _render_mermaid(self, parent: str, children: List[Dict], depth: int = 0) -> str:
        lines = []
        for child in children:
            name = child.get("name", f"Node{depth}") if isinstance(child, dict) else str(child)
            sp = self._sanitize(parent)
            sn = self._sanitize(name)
            lines.append(f'    {sp}["{parent}"] --> {sn}["{name}"]')
            if isinstance(child, dict) and child.get("children"):
                lines.append(self._render_mermaid(name, child["children"], depth + 1))
        return "\n".join(lines)

    def _sanitize(self, text: str) -> str:
        """清理 mermaid 节点名中的特殊字符"""
        return text.replace(" ", "_").replace('"', "'").replace("[", "").replace("]", "")

    # ═══════════════════════════════════════════════════════════
    #  测验题目（考官）
    # ═══════════════════════════════════════════════════════════
    def generate_quiz(self, content: Dict[str, Any]) -> str:
        """格式化测验"""
        md = "# 测验与评估\n\n"
        for i, q in enumerate(content.get("questions", []), 1):
            md += f"## 选择题 {i}\n\n**{q.get('question', '')}**\n\n"
            for opt in q.get("options", []):
                md += f"- {opt}\n"
            ans = q.get("answer", 0)
            if isinstance(ans, int):
                ans_letter = chr(65 + ans)  # 0→A, 1→B, ...
            else:
                ans_letter = str(ans)
            md += f"\n> ✅ 答案: {ans_letter}  \n> 💡 解析: {q.get('explanation', '')}\n\n"
        for i, eq in enumerate(content.get("essayQuestions", []), 1):
            md += f"## 简答题 {i}（{eq.get('maxPoints', 10)}分）\n\n{eq.get('question', '')}\n\n"
        return md

    # ═══════════════════════════════════════════════════════════
    #  代码教程（极客）
    # ═══════════════════════════════════════════════════════════
    def generate_code_tutorial(self, content: Dict[str, Any]) -> str:
        """格式化代码教程
        兼容 v1 格式: exercises 为字符串数组
        兼容 v2 旧格式: exercises 为对象数组
        """
        md = f"# {content.get('title', '编程示例')}\n\n{content.get('description', '')}\n\n"
        if content.get("code"):
            md += f"## 示例代码\n\n```\n{content['code']}\n```\n\n"
        if content.get("expected_output"):
            md += f"**预期输出**: `{content['expected_output']}`\n\n"
        for i, ex in enumerate(content.get("exercises", []), 1):
            if isinstance(ex, str):
                md += f"## 练习 {i}: {ex}\n\n"
            elif isinstance(ex, dict):
                md += f"## 练习 {i}: {ex.get('title', '')}\n\n"
                md += f"{ex.get('description', '')}\n\n"
                md += f"- **要求**: {ex.get('requirement', '')}\n"
                md += f"- **提示**: {ex.get('hint', '')}\n\n"
        return md

    # ═══════════════════════════════════════════════════════════
    #  视频脚本（导演）
    # ═══════════════════════════════════════════════════════════
    def generate_video_script(self, content: Dict[str, Any]) -> str:
        """格式化视频脚本
        兼容 v1 格式: scenes 中包含 resources 数组
        """
        scenes = content.get("scenes", [])
        total = sum(s.get("duration_seconds", 0) for s in scenes)
        md = f"# 视频脚本（总时长: {total}秒）\n\n"
        for scene in scenes:
            sn = scene.get("scene_number", "?")
            md += f"## 场景 {sn}: {scene.get('title', '')}（{scene.get('duration_seconds', 0)}秒）\n\n"
            md += f"**视觉**: {scene.get('visual', '')}\n\n"
            md += f"**旁白**: {scene.get('voiceover', '')}\n\n"
            # v1 格式：resources
            if scene.get("resources"):
                md += "**相关资源**:\n"
                for res in scene["resources"]:
                    if isinstance(res, dict):
                        md += f"- [{res.get('title', 'Resource')}]({res.get('url', '#')}) ({res.get('platform', '')}, {res.get('duration', '')})\n"
                md += "\n"
            md += "---\n\n"
        return md

    # ═══════════════════════════════════════════════════════════
    #  审查报告（审查员）
    # ═══════════════════════════════════════════════════════════
    def generate_review_report(self, content: Dict[str, Any]) -> str:
        """格式化审查报告"""
        md = "# 质量审查报告\n\n"
        qs = content.get('quality_score', 'N/A')
        qs_display = f"{qs}/100" if isinstance(qs, (int, float)) and qs <= 100 else str(qs)
        md += f"- **质量评分**: {qs_display}\n"
        md += f"- **幻觉风险**: {content.get('hallucination_risk', 'N/A')}\n"
        md += f"- **难度评估**: {content.get('difficulty_assessment', 'N/A')}\n"
        summary = content.get("review_summary", "")
        if summary:
            md += f"\n## 总体评价\n\n{summary}\n\n"
        if content.get("suggestions"):
            md += "## 改进建议\n\n"
            for s in content["suggestions"]:
                md += f"- {s}\n"
        return md

    # ═══════════════════════════════════════════════════════════
    #  合并输出
    # ═══════════════════════════════════════════════════════════
    def generate_combined(self, all_results: Dict[str, Any]) -> str:
        """将所有 Agent 输出合并为完整 Markdown 文档"""
        md = "# EduNexus 智能教学内容生成报告\n\n"
        md += "> 本报告由 EduNexus v2.0 多智能体系统自动生成\n\n---\n\n"

        handlers = {
            "professor": self.generate_academic_content,
            "architect": self.generate_mindmap,
            "examiner": self.generate_quiz,
            "director": self.generate_video_script,
            "hacker": self.generate_code_tutorial,
            "reviewer": self.generate_review_report,
        }

        for agent_id, content in all_results.items():
            if agent_id == "manager" and isinstance(content, dict):
                md += "# 📋 任务规划\n\n"
                for task in content.get("tasks", []):
                    md += f"- {task}\n"
                if content.get("coordination_notes"):
                    md += "\n**协调说明**:\n"
                    for note in content["coordination_notes"]:
                        md += f"- {note}\n"
                md += "\n---\n\n"
                continue

            handler = handlers.get(agent_id)
            if handler and isinstance(content, dict):
                md += handler(content)
                md += "\n---\n\n"

        return md
