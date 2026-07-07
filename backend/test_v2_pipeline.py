"""
v2.0 Agent 管道集成测试

用法:
  1. 设置环境变量 DEEPSEEK_API_KEY=sk-xxx
  2. python test_v2_pipeline.py
"""
import os
import sys
import json

sys.path.insert(0, '.')

from app.agents import (
    AgentCoordinator, LangChainUtils,
    ManagerAgent, ProfessorAgent, ArchitectAgent,
    ExaminerAgent, DirectorAgent, HackerAgent, ReviewerAgent,
    MarkdownGeneratorTool,
)

def main():
    topic = "Transformer 架构中的注意机制"

    # 初始化 DeepSeek
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        LangChainUtils.initialize_model(api_key, "deepseek-chat")
        print("[INIT] DeepSeek model initialized ✓")
    else:
        print("[INIT] ⚠ DEEPSEEK_API_KEY not set — agents will fail at LLM call")
        print("       Set with: $env:DEEPSEEK_API_KEY='sk-xxx' (PowerShell)")
        return

    # 创建协调器
    coord = AgentCoordinator()
    coord.register_agent(ManagerAgent())
    coord.register_agent(ProfessorAgent())
    coord.register_agent(ArchitectAgent())
    coord.register_agent(ExaminerAgent())
    coord.register_agent(DirectorAgent())
    coord.register_agent(HackerAgent())
    coord.register_agent(ReviewerAgent())
    print("[INIT] 7 agents registered ✓")

    # 执行管道
    print(f"\n{'='*60}")
    print(f"  Pipeline: {topic}")
    print(f"{'='*60}\n")

    result = coord.execute_pipeline(topic)

    # 结果概览
    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}\n")

    for r in result["results"]:
        status_icon = "✓" if r.status.value == "success" else "✗"
        print(f"  [{status_icon}] {r.agent_id:12s}  {r.status.value:8s}  {r.duration:5d}ms")
        if r.error:
            print(f"       Error: {r.error[:100]}")

    # 累积上下文
    print(f"\n  Accumulated context keys: {list(result['accumulated_context'].keys())}")
    print(f"  Task ID: {result['task_id']}")

    # 生成 Markdown 报告
    md_tool = MarkdownGeneratorTool()
    markdown = md_tool.generate_combined(result["accumulated_context"])

    # 保存报告
    report_path = f"v2_report_{result['task_id']}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"\n  Markdown report saved to: {report_path}")

    # 输出摘要
    print(f"\n{'='*60}")
    print(f"  Report Preview (first 500 chars)")
    print(f"{'='*60}\n")
    print(markdown[:500])

if __name__ == "__main__":
    main()
