"""
代码执行工具 — Python 安全沙箱

让 HackerAgent 可以在生成代码后自动验证其正确性。
Agent 写出代码 → 工具执行 → 返回输出 → Agent 根据输出修正错误。

安全措施:
  - subprocess 隔离（独立进程）
  - 超时限制（默认 30 秒）
  - 禁用危险模块（os, sys, subprocess, shutil 等通过 AST 检测）

使用方式:
    from .tools.code_executor import code_executor_tool
    agent = model.bind_tools([code_executor_tool])
"""
import ast
import logging
import subprocess
import tempfile
import os
from typing import Optional

logger = logging.getLogger("edunexus.agents")

# 延迟导入
_tool_available = False
try:
    from langchain_core.tools import tool as _tool_decorator
    _tool_available = True
except ImportError:
    _tool_available = False

# 危险模块黑名单
DANGEROUS_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "socket", "requests",
    "urllib", "http", "ftplib", "telnetlib", "smtplib",
    "pathlib", "glob", "fnmatch", "importlib",
}


def _validate_code_safety(code: str) -> Optional[str]:
    """
    AST 静态分析：检测代码中的危险导入和调用。

    Returns:
        None 表示安全，str 表示发现的危险操作描述
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"语法错误: {e}"

    for node in ast.walk(tree):
        # 检测危险 import
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in DANGEROUS_IMPORTS:
                    return f"禁止导入危险模块: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in DANGEROUS_IMPORTS:
                return f"禁止从危险模块导入: {node.module}"

        # 检测危险函数调用
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec", "compile", "__import__", "open"}:
                    return f"禁止调用危险函数: {node.func.id}()"

    return None  # 安全


def _create_code_executor_tool():
    """创建代码执行 @tool"""
    if not _tool_available:
        return None

    @_tool_decorator
    def execute_python(code: str, timeout: int = 30) -> str:
        """在安全沙箱中执行 Python 代码并返回标准输出。

        用于验证代码示例的正确性和获取实际运行结果。
        支持 import 常用科学计算/数据处理库（numpy, pandas, torch, matplotlib 等）。

        Args:
            code: 完整的 Python 代码（含 import 语句）
            timeout: 执行超时时间（秒），默认 30

        Returns:
            标准输出内容，或错误信息
        """
        # 1. 静态安全检查
        safety_issue = _validate_code_safety(code)
        if safety_issue:
            return f"⛔ 安全检查未通过: {safety_issue}"

        # 2. 写入临时文件执行
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                temp_path = f.name

            # 3. 子进程隔离执行
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
                env={
                    **os.environ,
                    "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                },
            )

            output = result.stdout
            if result.stderr:
                output += f"\n\n[stderr]:\n{result.stderr[:1000]}"
            if result.returncode != 0:
                output += f"\n\n[exit code]: {result.returncode}"

            return output.strip() if output.strip() else "(无输出)"

        except subprocess.TimeoutExpired:
            return f"⏱ 代码执行超时 ({timeout}秒)"
        except Exception as e:
            return f"❌ 执行错误: {type(e).__name__}: {e}"
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except (OSError, UnboundLocalError):
                pass

    return execute_python


code_executor_tool = _create_code_executor_tool()
