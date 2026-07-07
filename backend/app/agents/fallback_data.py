"""
共享 Fallback 数据 — v2 Agent LLM 调用失败时的兜底 Mock 数据
格式与 v1.0.0 ContentGenerator._get_fallback() 完全对齐，保证前端正常渲染
"""
from typing import Dict, Any


def get_fallback_content(agent_type: str, topic: str) -> Dict[str, Any]:
    """返回 v1 兼容格式的 mock 内容"""

    if agent_type == "manager":
        return {
            "tasks": [
                f"确定「{topic}」的教学目标和核心知识点",
                f"设计「{topic}」的课程大纲与知识结构",
                f"编写「{topic}」的详细教学内容与示例",
                f"创建「{topic}」的评估题目和答案",
                f"制作「{topic}」的教学视频脚本",
                f"开发「{topic}」的互动练习与代码案例",
                f"审核并优化「{topic}」的全部教学材料",
            ],
            "priority": ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
            "coordination_notes": [
                "教授智能体应在架构师之前生成基础内容",
                "考官智能体应基于教授的内容设计题目",
                "导演智能体需要基于架构师的结构制作脚本",
            ],
        }

    if agent_type == "professor":
        return {
            "title": f"深入理解：{topic}",
            "sections": [
                {
                    "heading": "基础概念与原理",
                    "subsections": [
                        {
                            "subheading": "核心定义",
                            "body": f"{topic}是该领域的核心概念之一。在深入探讨之前，我们先建立对基础原理的清晰理解。这一概念源于对实际问题的深入思考，经过多年的理论发展和实践验证，已经成为现代技术体系中不可或缺的组成部分。理解其核心定义是掌握整个知识体系的基石。",
                        },
                        {
                            "subheading": "理论基础",
                            "body": f"{topic}的数学基础建立在严谨的理论框架之上。理解其中的理论推导对于掌握该概念至关重要。理论基础不仅帮助我们解释现象，更指导着实践应用的方向。从基本原理出发，我们可以逐步推导出更为复杂的应用模式。",
                        },
                    ],
                },
                {
                    "heading": "实践应用与案例分析",
                    "subsections": [
                        {
                            "subheading": "应用场景",
                            "body": f"在实际应用中，{topic}已经被广泛部署于各类场景。从工业界到学术界，从基础研究到商业产品，都能看到它的身影。我们将通过具体案例来分析其工作原理，帮助你建立理论与实践之间的桥梁。",
                        },
                        {
                            "subheading": "常见误区",
                            "body": f"学习{topic}的过程中，最常遇到的困惑包括概念混淆、参数调优不当、以及对其适用范围的误判。本节将逐一澄清这些误区，帮助你避开学习过程中的常见陷阱，建立正确的认知框架。",
                        },
                    ],
                },
                {
                    "heading": "进阶主题与前沿发展",
                    "subsections": [
                        {
                            "subheading": "最新研究动态",
                            "body": f"近年来，围绕{topic}的研究取得了突破性进展。新的方法和优化策略不断涌现，推动了整个领域向前发展。关注最新研究动态，有助于把握技术演进的方向，为深入学习和创新实践提供灵感。",
                        },
                        {
                            "subheading": "与其他领域的交叉",
                            "body": f"{topic}并非孤立存在，它与多个相关领域有着深刻的联系。理解这些交叉关系，不仅能够加深对核心概念的理解，还能激发跨领域的创新思考。跨学科的知识整合是解决复杂问题的关键能力。",
                        },
                    ],
                },
            ],
        }

    if agent_type == "architect":
        return {
            "mindmap": {
                "root": f"root(({topic}))",
                "children": [
                    {
                        "name": "基础理论",
                        "children": [
                            {"name": "核心定义与概念"},
                            {"name": "数学原理与推导"},
                            {"name": "历史发展与演进"},
                        ],
                    },
                    {
                        "name": "算法与实现",
                        "children": [
                            {"name": "核心算法流程"},
                            {"name": "Python代码实现"},
                            {"name": "性能优化技巧"},
                            {"name": "常见变体与改进"},
                        ],
                    },
                    {
                        "name": "应用场景",
                        "children": [
                            {"name": "工业界应用案例"},
                            {"name": "学术研究方向"},
                            {"name": "未来发展趋势"},
                        ],
                    },
                    {
                        "name": "关键特性与优势",
                        "children": [
                            {"name": "与传统方法的对比"},
                            {"name": "可扩展性与灵活性"},
                            {"name": "实践中的最佳做法"},
                        ],
                    },
                ],
            }
        }

    if agent_type == "examiner":
        return {
            "questions": [
                {
                    "question": f"关于{topic}，以下哪个描述最准确？",
                    "options": [
                        f"A. {topic}仅适用于特定领域的问题",
                        f"B. {topic}是一种通用的解决方案，核心在于其理论基础的普适性",
                        f"C. {topic}已经过时，被新技术完全取代",
                        f"D. {topic}只具有理论价值，没有实际应用",
                    ],
                    "answer": 1,
                    "explanation": f"{topic}的核心理论具有普适性，能够应用于多个不同领域的问题。虽然在不同场景下需要适当调整，但其基本原理是通用的。",
                },
                {
                    "question": f"在{topic}的实践中，以下哪个步骤应该首先完成？",
                    "options": [
                        "A. 参数调优与模型优化",
                        "B. 数据收集与预处理",
                        "C. 模型部署与上线",
                        "D. 结果可视化与报告",
                    ],
                    "answer": 1,
                    "explanation": "数据收集与预处理是所有后续步骤的基础。没有高质量的数据，任何算法都无法发挥其应有的效果。",
                },
                {
                    "question": f"{topic}与传统方法相比，最主要的优势是什么？",
                    "options": [
                        "A. 计算速度更快",
                        "B. 理论基础更先进，能够处理更复杂的场景",
                        "C. 实现更简单",
                        "D. 不需要任何数据",
                    ],
                    "answer": 1,
                    "explanation": f"{topic}建立了更先进的理论框架，能够处理传统方法难以应对的复杂场景。这是其最本质的优势。",
                },
            ],
        }

    if agent_type == "director":
        return {
            "scenes": [
                {
                    "scene_number": 1,
                    "title": f"{topic}基础介绍",
                    "visual": f"动画展示一个与{topic}相关的实际问题场景，通过可视化的方式引入核心概念",
                    "voiceover": f"今天我们来探索{topic}。从一个直观的问题开始，让我们逐步理解它的核心思想。无论你是否有相关基础，这个讲解都将帮助你建立起清晰的概念框架。",
                    "duration_seconds": 45,
                    "resources": [
                        {
                            "type": "video",
                            "title": f"{topic} - 从零开始的完整教程",
                            "description": f"全面了解{topic}的基本概念、核心原理和实际应用场景，适合初学者入门",
                            "thumbnail": f"https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg",
                            "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+tutorial",
                            "duration": "15:00",
                            "platform": "YouTube",
                        }
                    ],
                },
                {
                    "scene_number": 2,
                    "title": f"{topic}核心原理深度解析",
                    "visual": f"逐步拆解{topic}的核心算法流程，用动画展示关键步骤的数学原理",
                    "voiceover": f"让我们深入到{topic}的核心。理解它的工作原理，就像解开一个精妙的谜题。每一个步骤都有其深刻的设计意图，我们将一一揭示这些设计的巧妙之处。",
                    "duration_seconds": 60,
                    "resources": [
                        {
                            "type": "video",
                            "title": f"{topic}核心原理详解 - 深入理解每个细节",
                            "description": f"深入理解{topic}的工作原理、数学基础和实现细节，适合有一定基础的学习者",
                            "thumbnail": f"https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg",
                            "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+deep+dive",
                            "duration": "20:00",
                            "platform": "YouTube",
                        }
                    ],
                },
                {
                    "scene_number": 3,
                    "title": f"{topic}实战应用与代码演示",
                    "visual": f"实际案例演示和代码实现，展示{topic}在真实场景中的运用",
                    "voiceover": f"通过实际案例掌握{topic}的应用，理论结合实践是最有效的学习方式。我们将从头开始构建一个完整的示例，让你看到理论是如何转化为实际代码的。",
                    "duration_seconds": 75,
                    "resources": [
                        {
                            "type": "video",
                            "title": f"{topic}实战项目 - 从理论到代码实现",
                            "description": f"通过实际项目学习{topic}的具体实现、最佳实践和行业应用",
                            "thumbnail": f"https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg",
                            "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+implementation",
                            "duration": "25:00",
                            "platform": "YouTube",
                        }
                    ],
                },
            ],
        }

    if agent_type == "hacker":
        return {
            "title": f"{topic} - Python代码实验",
            "description": f"通过动手实践来理解{topic}的核心原理，代码是最好的老师",
            "code": f'''"""
{topic} - 动手实验
通过代码来直观理解核心概念
"""
import numpy as np
import matplotlib.pyplot as plt


def demonstrate_concept():
    """演示{topic}的核心概念"""
    # ===== 步骤1: 准备数据 =====
    print("步骤1: 准备实验数据")
    x = np.linspace(-5, 5, 100)
    y = x ** 2  # 示例：二次函数

    # ===== 步骤2: 核心计算 =====
    print("步骤2: 执行核心计算")
    derivative = 2 * x  # 导数
    gradient = derivative[50]  # 某点的梯度

    print(f"在 x=0 处的梯度: {{gradient}}")

    # ===== 步骤3: 可视化 =====
    print("步骤3: 生成可视化图表")
    # plt.plot(x, y, label='f(x)')
    # plt.legend()
    # plt.show()

    return {{"min_value": np.min(y), "gradient_at_zero": float(gradient)}}


if __name__ == "__main__":
    result = demonstrate_concept()
    print(f"实验结果: {{result}}")
''',
            "expected_output": f"步骤1: 准备实验数据\n步骤2: 执行核心计算\n在 x=0 处的梯度: 0.0\n步骤3: 生成可视化图表\n实验结果: {{'min_value': 0.0, 'gradient_at_zero': 0.0}}",
            "exercises": [
                f"修改函数定义，尝试其他函数来探索{topic}的不同行为",
                f"添加噪声数据，观察{topic}对噪声的鲁棒性",
                f"实现{topic}的一个变体算法，比较两者的性能差异",
            ],
        }

    if agent_type == "reviewer":
        return {
            "hallucination_risk": "low",
            "quality_score": 85,
            "suggestions": [
                "建议在教授文档中增加更多实际案例，帮助学习者建立直观理解",
                "思维导图可以进一步细化第三级节点，增强知识结构的完整性",
                "代码实验部分可以增加更多交互式练习，提升动手实践的效果",
            ],
            "difficulty_assessment": "内容难度适中，适合有一定基础的学习者。建议初学者先补充相关前置知识。",
        }

    # 未知 agent_type
    return {"message": f"Agent '{agent_type}' fallback content for topic: {topic}"}
