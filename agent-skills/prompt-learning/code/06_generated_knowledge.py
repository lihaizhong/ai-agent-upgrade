"""
06 - 生成知识提示 (Generated Knowledge Prompting)

生成知识提示让模型先生成相关知识，再基于知识回答问题。
核心：两阶段处理

阶段1（生成知识）：让模型先想相关的已知信息
阶段2（基于知识回答）：基于生成的知识给出最终答案

适用场景：需要模型固有知识的问题、避免幻觉
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


def generated_knowledge_prompt(question: str) -> dict:
    """生成知识提示实现"""
    # 阶段1：生成相关知识
    phase1_prompt = f"""在回答这个问题之前，请先列出你知道的与问题相关的所有背景知识。

问题：{question}

请列出所有可能有助于回答这个问题的背景知识、事实、定义或概念。"""

    result1 = call_llm(phase1_prompt, temperature=0.7)
    if not result1["success"]:
        return {"success": False, "error": "阶段1失败"}

    knowledge = result1["data"]

    # 阶段2：基于知识回答
    phase2_prompt = f"""基于以下背景知识，回答问题。

背景知识：
{knowledge}

问题：{question}

请基于上述背景知识，给出准确、详细的回答。"""

    result2 = call_llm(phase2_prompt)

    return {
        "success": True,
        "knowledge": knowledge,
        "answer": result2["data"] if result2["success"] else result2["error"],
        "knowledge_tokens": result1.get("usage", 0),
        "answer_tokens": result2.get("usage", 0) if result2["success"] else 0,
    }


def compare_with_baseline(question: str):
    """对比有/无生成知识的效果"""
    print("\n" + "=" * 60)
    print("对比：有生成知识 vs 无生成知识")
    print("=" * 60)

    # 无生成知识（直接回答）
    baseline_result = call_llm(question)
    print(f"\n【直接回答】\n{question}")
    print("-" * 40)
    if baseline_result["success"]:
        print(baseline_result["data"][:300] + "...")

    # 有生成知识
    gk_result = generated_knowledge_prompt(question)
    print(f"\n【生成知识提示】")
    print("-" * 40)
    if gk_result["success"]:
        print(f"【生成的知识】\n{gk_result['knowledge'][:200]}...")
        print(f"\n【最终答案】\n{gk_result['answer'][:300]}...")

    return gk_result


def main():
    print("=" * 60)
    print("生成知识提示 (Generated Knowledge) 示例")
    print("=" * 60)

    questions = ["解释为什么天空是蓝色的", "为什么地球会有四季变化"]

    for q in questions:
        compare_with_baseline(q)
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
