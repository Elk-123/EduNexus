"""
Markdown 生成工具 — 将 Agent 输出格式化为结构化 Markdown 文档
"""
from typing import Dict, Any, List


class MarkdownGeneratorTool:
    """Markdown 格式化器 — 将各 Agent 的 JSON 输出转为可读 Markdown"""

    def generate_academic_content(self, content: Dict[str, Any]) -> str:
        """格式化教授智能体输出的学术内容"""
        md = f"# {content.get('title', '教学内容')}\n\n"
        for section in content.get("sections", []):
            md += f"## {section.get('heading', '章节')}\n\n{section.get('body', '')}\n\n"
        if content.get("keyConcepts"):
            md += "## 关键概念\n\n"
            for c in content["keyConcepts"]:
                if isinstance(c, dict):
                    md += f"- **{c.get('name', '')}**: {c.get('explanation', '')}\n"
                else:
                    md += f"- {c}\n"
        if content.get("references"):
            md += "\n## 参考文献\n\n"
            for ref in content["references"]:
                md += f"- [{ref.get('title', 'Ref')}]({ref.get('url', '#')})\n"
        return md

    def generate_mindmap(self, content: Dict[str, Any]) -> str:
        """格式化思维导图"""
        md = f"# 知识结构: {content.get('root', '主题')}\n\n```mermaid\ngraph TD\n"
        md += self._render_mermaid(content.get("root", "root"), content.get("children", []))
        md += "\n```\n"
        return md

    def _render_mermaid(self, parent: str, children: List[Dict], depth: int = 0) -> str:
        lines = []
        for child in children:
            name = child.get("name", f"Node{depth}")
            sp = parent.replace(" ", "_")
            sn = name.replace(" ", "_")
            lines.append(f'    {sp}["{parent}"] --> {sn}["{name}"]')
            if child.get("children"):
                lines.append(self._render_mermaid(name, child["children"], depth + 1))
        return "\n".join(lines)

    def generate_quiz(self, content: Dict[str, Any]) -> str:
        """格式化测验"""
        md = "# 测验与评估\n\n"
        for i, q in enumerate(content.get("questions", []), 1):
            md += f"## 选择题 {i}\n\n**{q.get('question', '')}**\n\n"
            for opt in q.get("options", []):
                md += f"- {opt}\n"
            md += f"\n> ✅ 答案: {q.get('answer', '')}  \n> 💡 解析: {q.get('explanation', '')}\n\n"
        for i, eq in enumerate(content.get("essayQuestions", []), 1):
            md += f"## 简答题 {i}（{eq.get('maxPoints', 10)}分）\n\n{eq.get('question', '')}\n\n"
        return md

    def generate_code_tutorial(self, content: Dict[str, Any]) -> str:
        """格式化代码教程"""
        md = f"# {content.get('title', '编程示例')}\n\n{content.get('description', '')}\n\n"
        if content.get("code"):
            md += f"## 示例代码\n\n```\n{content['code']}\n```\n\n"
        if content.get("expected_output"):
            md += f"**预期输出**: `{content['expected_output']}`\n\n"
        for i, ex in enumerate(content.get("exercises", []), 1):
            md += f"## 练习 {i}: {ex.get('title', '')}\n\n"
            md += f"{ex.get('description', '')}\n\n"
            md += f"- **要求**: {ex.get('requirement', '')}\n"
            md += f"- **提示**: {ex.get('hint', '')}\n\n"
        return md

    def generate_video_script(self, content: Dict[str, Any]) -> str:
        """格式化视频脚本"""
        total = content.get("total_duration", 0)
        md = f"# 视频脚本（总时长: {total}秒）\n\n"
        for scene in content.get("scenes", []):
            sn = scene.get("scene_number", "?")
            md += f"## 场景 {sn}: {scene.get('title', '')}（{scene.get('duration_seconds', 0)}秒）\n\n"
            md += f"**视觉**: {scene.get('visual', '')}\n\n"
            md += f"**旁白**: {scene.get('voiceover', '')}\n\n---\n\n"
        return md

    def generate_review_report(self, content: Dict[str, Any]) -> str:
        """格式化审查报告"""
        md = "# 质量审查报告\n\n"
        md += f"- **质量评分**: {content.get('quality_score', 'N/A')}/10\n"
        md += f"- **幻觉风险**: {content.get('hallucination_risk', 'N/A')}\n"
        md += f"- **难度评估**: {content.get('difficulty_assessment', 'N/A')}\n"
        md += f"\n## 总体评价\n\n{content.get('review_summary', '')}\n\n"
        if content.get("suggestions"):
            md += "## 改进建议\n\n"
            for s in content["suggestions"]:
                md += f"- {s}\n"
        return md

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
                md += "\n---\n\n"
                continue

            handler = handlers.get(agent_id)
            if handler and isinstance(content, dict):
                md += handler(content)
                md += "\n---\n\n"

        return md
