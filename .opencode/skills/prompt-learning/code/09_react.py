"""
09 - ReAct 框架 (Reason + Act)

ReAct 结合推理和行动，让模型能够与环境交互。
核心循环：思考 → 行动 → 观察 → 重复

适用场景：
- 需要使用工具的任务
- 需要环境反馈的决策
- 复杂的多步骤任务

注意：这是一个模拟框架，展示了 ReAct 的核心逻辑。
实际应用中需要与真实的工具 API 集成。
"""

from utils import call_llm
from enum import Enum


class Action(Enum):
    SEARCH = "search"
    CALCULATE = "calculate"
    LOOKUP = "lookup"
    ANSWER = "answer"


def react_loop(question: str, max_iterations: int = 5) -> dict:
    """ReAct 推理循环"""

    prompt_template = """你是一个助手，能够进行推理和执行行动。
你可以使用以下工具：
- search: 搜索信息
- calculate: 计算数学表达式
- lookup: 查询特定事实
- answer: 给出最终答案

当前问题：{question}

{context}

请按以下格式进行推理：

思考：我需要...
行动：search/calculate/lookup/answer
行动输入：...
观察：（等待行动结果）

开始："""

    context = ""
    iterations = []

    for i in range(max_iterations):
        print(f"\n{'=' * 40}")
        print(f"迭代 {i + 1}/{max_iterations}")
        print(f"{'=' * 40}")

        prompt = prompt_template.format(
            question=question, context=context if context else "（无前期上下文）"
        )

        result = call_llm(prompt, temperature=0.7)
        if not result["success"]:
            break

        response = result["data"]
        print(f"\n推理过程：\n{response}")
        iterations.append(response)

        if "answer" in response.lower():
            break

        context += f"\n\n{response}\n\n观察：根据上述推理和行动，下一步："

    return {
        "success": True,
        "iterations": iterations,
        "final_response": iterations[-1] if iterations else "未得到答案",
    }


def search_simulator(query: str) -> str:
    """模拟搜索功能"""
    return f"搜索结果：关于「{query}」的信息（这是模拟结果）"


def calculate_simulator(expr: str) -> str:
    """模拟计算功能"""
    try:
        result = eval(expr)
        return f"计算结果：{result}"
    except:
        return "计算表达式无效"


def lookup_simulator(entity: str) -> str:
    """模拟查询功能"""
    return f"查询结果：{entity}的相关信息（这是模拟结果）"


def main():
    print("=" * 60)
    print("ReAct 框架 (Reason + Act) 示例")
    print("=" * 60)

    questions = ["北京的人口是多少？比上海多还是少？", "计算 (15 + 25) * 3 的结果"]

    for q in questions:
        print(f"\n【问题】{q}")
        result = react_loop(q)
        if result["success"]:
            print(f"\n完成！共 {len(result['iterations'])} 次迭代")


if __name__ == "__main__":
    main()
