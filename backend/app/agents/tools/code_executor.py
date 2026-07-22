"""
代码执行工具 — v2.3: LangChain 标准 StructuredTool 包装
沙箱: subprocess 隔离 + AST 安全检查 + 超时控制

注意: langchain_experimental 中的 PythonREPLTool 未安装，保留自实现。
      当 langchain_experimental 可用后切换: from langchain_experimental.tools import PythonREPLTool
"""
import ast
import logging
import subprocess
import tempfile
import os
from typing import Optional

logger = logging.getLogger("edunexus.agents")

DANGEROUS_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "socket", "requests",
    "urllib", "http", "ftplib", "telnetlib", "smtplib",
    "pathlib", "glob", "fnmatch", "importlib",
}

_tool_instance = None


def _validate_code_safety(code: str) -> Optional[str]:
    """AST 静态分析：检测危险导入和调用。返回 None 表示安全。"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Syntax error: {e}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in DANGEROUS_IMPORTS:
                    return f"禁止导入: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in DANGEROUS_IMPORTS:
                return f"禁止导入: {node.module}"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec", "compile", "__import__", "open"}:
                    return f"禁止调用: {node.func.id}()"
    return None


def get_code_executor():
    """获取 code_executor 工具实例（LangChain StructuredTool）"""
    global _tool_instance
    if _tool_instance is not None:
        return _tool_instance

    from langchain_core.tools import tool as _tool_dec

    @_tool_dec
    def execute_python(code: str, timeout: int = 30) -> str:
        """Execute Python code in a sandbox and return stdout/stderr.

        Use this to verify Python code examples work correctly.
        Supports standard libraries and common scientific packages (numpy, pandas, matplotlib).
        Do NOT use for system-level operations — those are blocked.

        Args:
            code: Complete Python source code with imports
            timeout: Max execution time in seconds (default 30)
        """
        safety_issue = _validate_code_safety(code)
        if safety_issue:
            return f"⛔ Safety check failed: {safety_issue}"

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(
                ["python", temp_path],
                capture_output=True, text=True, timeout=timeout,
                cwd=tempfile.gettempdir(),
                env={**os.environ, "PYTHONPATH": os.environ.get("PYTHONPATH", "")},
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]:\n{result.stderr[:1000]}"
            if result.returncode != 0:
                output += f"\n[exit code]: {result.returncode}"
            return output.strip() or "(no output)"

        except subprocess.TimeoutExpired:
            return f"⏱ Timeout after {timeout}s"
        except Exception as e:
            return f"❌ Execution error: {type(e).__name__}: {e}"
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

    _tool_instance = execute_python
    return _tool_instance


# 模块导入时直接初始化
code_executor_tool = get_code_executor()


# ═══════════════════════════════════════════════════════════════
#  [v2.2 legacy] 旧 code_executor.py — 见 git history: ea8a7c4
# ═══════════════════════════════════════════════════════════════
