"""
13 - 主动提示 (Active-Prompt)

主动提示根据问题的不确定性选择最有效的示例。
核心：计算每个问题的推理不确定性，选择最需要示例的问题。

工作流程：
1. 对多个问题进行推理
2. 计算推理结果的一致性/分歧度
3. 选择一致性最低的问题优先获取示例
"""

from utils import call_llm
from collections import Counter


def calculate_disagreement(responses: list) -> float:
    """计算响应之间的分歧度"""
    if not responses:
        return 0.0

    answers = [r.strip().lower() for r in responses]
    counter = Counter(answers)

    most_common_count = counter.most_common(1)[0][1]
    total = len(answers)

    disagreement = 1.0 - (most_common_count / total)
    return disagreement


def active_prompt_select(problems: list, n_select: int = 3) -> dict:
    """主动提示选择：选择最需要示例的问题"""
    print("=" * 60)
    print("主动提示 (Active-Prompt) - 问题选择")
    print("=" * 60)

    print(f"\n对 {len(problems)} 个问题进行初步推理...")

    problem_stats = []

    for i, problem in enumerate(problems):
        print(f"\n问题 {i + 1}: {problem[:50]}...")

        responses = []
        for trial in range(5):
            prompt = f"{problem}\n\n让我们一步步思考。"
            result = call_llm(prompt, temperature=0.8)

            if result["success"]:
                responses.append(result["data"])

        disagreement = calculate_disagreement(responses)

        print(f"  推理次数: {len(responses)}")
        print(f"  分歧度: {disagreement:.2f}")

        problem_stats.append(
            {"problem": problem, "disagreement": disagreement, "responses": responses}
        )

    problem_stats.sort(key=lambda x: x["disagreement"], reverse=True)

    selected = problem_stats[:n_select]

    print("\n" + "=" * 60)
    print(f"选择了 {n_select} 个分歧度最高的问题作为示例候选：")
    for i, item in enumerate(selected):
        print(f"\n{i + 1}. 分歧度: {item['disagreement']:.2f}")
        print(f"   问题: {item['problem'][:80]}...")

    return {
        "all_problems": problems,
        "selected": selected,
        "sorted_by_disagreement": problem_stats,
    }


def main():
    problems = [
        "明天的天气会怎么样？",
        "这家餐厅的菜好不好吃？",
        "如果所有的鸟都会飞，企鹅是一种鸟，企鹅会飞吗？",
        "地球是圆的还是平的？",
        "人工智能会取代人类工作吗？",
    ]

    result = active_prompt_select(problems, n_select=3)


if __name__ == "__main__":
    main()
