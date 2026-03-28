"""
04 - 自我一致性 (Self-Consistency)

自我一致性通过多次采样和投票提高答案可靠性。
核心思想：多想几遍，少数服从多数。

实现步骤：
1. 对同一问题多次采样（温度 > 0）
2. 从每次回复中提取答案
3. 投票选出最一致的答案

适用场景：高准确性要求、复杂推理、数学计算
"""

import re
from utils import call_llm, extract_answer, vote_most_common


def self_consistency(
    question: str, n_samples: int = 10, temperature: float = 0.7, use_cot: bool = True
) -> dict:
    """
    自我一致性实现

    Args:
        question: 问题
        n_samples: 采样次数
        temperature: 温度参数（需要 > 0 以获得不同答案）
        use_cot: 是否使用思维链

    Returns:
        包含最终答案、投票结果的字典
    """
    # 构建提示词
    if use_cot:
        prompt = f"{question}\n\n让我们一步步思考。"
    else:
        prompt = question

    answers = []
    reasoning_steps = []

    print(f"开始自我一致性采样（{n_samples}次）...")

    for i in range(n_samples):
        result = call_llm(prompt, temperature=temperature)

        if result["success"]:
            response = result["data"]
            answer = extract_answer(response)
            answers.append(answer)
            reasoning_steps.append(response)

            if (i + 1) % 5 == 0:
                print(f"  已完成 {i + 1}/{n_samples} 次采样")

    # 投票
    final_answer, vote_count, total = vote_most_common(answers)

    return {
        "final_answer": final_answer,
        "vote_count": vote_count,
        "total_samples": total,
        "confidence": vote_count / total,
        "all_answers": answers,
        "reasoning_steps": reasoning_steps,
    }


def math_example():
    """数学问题示例"""
    question = """我6岁时，妹妹是我年龄的一半。
现在我70岁了，妹妹多大？"""

    return self_consistency(question, n_samples=10, temperature=0.7)


def logic_example():
    """逻辑问题示例"""
    question = """如果所有的鸟都会飞，企鹅是一种鸟，
那么企鹅会飞吗？请推理。"""

    return self_consistency(question, n_samples=8, temperature=0.7)


def main():
    print("=" * 60)
    print("自我一致性 (Self-Consistency) 示例")
    print("=" * 60)

    print("\n【示例】年龄问题")
    print("问题：我6岁时，妹妹是我年龄的一半。现在我70岁了，妹妹多大？")
    print("-" * 40)

    result = math_example()

    print(f"\n投票结果：")
    print(f"  最终答案：{result['final_answer']}")
    print(f"  得票：{result['vote_count']}/{result['total_samples']}")
    print(f"  置信度：{result['confidence'] * 100:.1f}%")

    print(f"\n所有采样答案：{result['all_answers']}")

    print("\n" + "-" * 40)
    print("推理过程示例（取第一个）：")
    print(result["reasoning_steps"][0][:500] + "...")


if __name__ == "__main__":
    main()
