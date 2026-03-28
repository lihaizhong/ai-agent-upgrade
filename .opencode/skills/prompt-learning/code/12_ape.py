"""
12 - 自动提示工程师 (APE)

APE (Automatic Prompt Engineer) 自动生成和优化提示词。
核心：通过 LLM 生成多个候选提示，选择最优的。

工作流程：
1. 生成：基于任务描述生成多个候选提示
2. 评估：使用候选提示执行任务
3. 选择：选出效果最好的提示
"""

from utils import call_llm


def generate_candidate_prompts(task: str, n_candidates: int = 5) -> list:
    """生成候选提示"""
    prompt = f"""为以下任务生成 {n_candidates} 个不同的提示词。

任务：{task}

要求：
1. 每个提示词都应该能指导 AI 完成上述任务
2. 提示词应该清晰、具体、有指导性
3. 可以从不同角度或风格来设计

输出格式（每个提示词一行）：
1. [提示词1]
2. [提示词2]
...
{n_candidates}. [提示词{n_candidates}]"""

    result = call_llm(prompt, temperature=0.9)
    if not result["success"]:
        return []

    prompts = []
    for line in result["data"].split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            if "." in line:
                prompt_text = line.split(".", 1)[1].strip()
                prompts.append(prompt_text)

    return prompts[:n_candidates]


def evaluate_prompt(prompt: str, test_cases: list) -> dict:
    """评估提示词效果"""
    scores = []
    details = []

    for test_case in test_cases:
        full_prompt = f"{prompt}\n\n任务：{test_case['input']}"
        result = call_llm(full_prompt, temperature=0.3)

        if result["success"]:
            response = result["data"]
            expected = test_case.get("expected", "")

            similarity = calculate_similarity(response, expected)
            scores.append(similarity)
            details.append(
                {
                    "input": test_case["input"],
                    "expected": expected,
                    "actual": response[:100],
                    "similarity": similarity,
                }
            )

    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        "prompt": prompt,
        "avg_score": avg_score,
        "scores": scores,
        "details": details,
    }


def calculate_similarity(text1: str, text2: str) -> float:
    """简单相似度计算"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    overlap = len(words1 & words2)
    total = len(words1 | words2)

    return overlap / total if total > 0 else 0.0


def ape_optimize(task: str, test_cases: list, n_candidates: int = 5) -> dict:
    """APE 提示词优化流程"""
    print("=" * 60)
    print("APE 自动提示词优化")
    print("=" * 60)

    print("\n【步骤1】生成候选提示词...")
    candidates = generate_candidate_prompts(task, n_candidates)
    print(f"生成了 {len(candidates)} 个候选提示词")

    print("\n【步骤2】评估候选提示词...")
    results = []
    for i, candidate in enumerate(candidates):
        print(f"\n评估提示词 {i + 1}/{len(candidates)}...")
        eval_result = evaluate_prompt(candidate, test_cases)
        results.append(eval_result)
        print(f"  平均得分：{eval_result['avg_score']:.2f}")

    results.sort(key=lambda x: x["avg_score"], reverse=True)

    print("\n【步骤3】选择最优提示词")
    best = results[0]
    print(f"\n最优提示词（得分：{best['avg_score']:.2f}）：")
    print(f"  {best['prompt']}")

    return {
        "task": task,
        "candidates": candidates,
        "best_prompt": best["prompt"],
        "best_score": best["avg_score"],
        "all_results": results,
    }


def main():
    print("=" * 60)
    print("自动提示工程师 (APE) 示例")
    print("=" * 60)

    task = "让 AI 总结一篇文章的主要内容"
    test_cases = [
        {"input": "一篇关于人工智能发展趋势的文章", "expected": "总结 AI 发展趋势"},
        {"input": "一篇介绍新冠疫情影响的报道", "expected": "总结疫情影响"},
    ]

    result = ape_optimize(task, test_cases, n_candidates=3)


if __name__ == "__main__":
    main()
