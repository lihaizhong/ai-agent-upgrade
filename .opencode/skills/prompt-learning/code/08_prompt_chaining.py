"""
08 - 链式提示 (Prompt Chaining)

链式提示将复杂任务分解为多个简单步骤，顺序执行。
核心：每个步骤的输出作为下一步的输入。

适用场景：
- 复杂多步骤任务
- 需要逐步处理的工作流
- 需要确保每步正确性

实现要点：
1. 清晰定义每个步骤
2. 设计步骤间的数据传递
3. 每步可独立验证
"""

from utils import call_llm


class PromptChain:
    def __init__(self):
        self.steps = []
        self.results = []

    def add_step(self, name: str, prompt_template: str, input_var: str):
        self.steps.append(
            {"name": name, "prompt_template": prompt_template, "input_var": input_var}
        )

    def execute(self, initial_input: str) -> dict:
        """执行链式提示"""
        current_input = initial_input
        results = []

        print(f"开始执行链式提示（共 {len(self.steps)} 步）\n")

        for i, step in enumerate(self.steps):
            print(f"【步骤 {i + 1}】{step['name']}")
            print("-" * 40)

            prompt = step["prompt_template"].replace(
                f"{{{step['input_var']}}}", current_input
            )
            result = call_llm(prompt)

            if result["success"]:
                output = result["data"]
                print(f"输出：{output[:200]}...")
                results.append(
                    {"step": step["name"], "input": current_input, "output": output}
                )
                current_input = output
            else:
                print(f"步骤失败：{result['error']}")
                return {
                    "success": False,
                    "error": f"步骤 {i + 1} 失败",
                    "results": results,
                }

            print()

        return {"success": True, "results": results, "final_output": current_input}


def document_analysis_example():
    """文档分析链式提示示例"""
    chain = PromptChain()

    chain.add_step(
        name="提取关键信息",
        prompt_template="""从以下文档中提取关键信息，包括：
1. 主要主题
2. 关键人物或实体
3. 重要日期或时间
4. 主要事件或结论

文档：{input}

请用结构化格式输出。""",
        input_var="input",
    )

    chain.add_step(
        name="生成摘要",
        prompt_template="""基于以下文档内容和提取的关键信息，
生成一份简洁的摘要（不超过100字）。

文档关键信息：
{input}

摘要：""",
        input_var="input",
    )

    chain.add_step(
        name="提出问题",
        prompt_template="""基于以下文档摘要，提出3个可能的后续研究问题。

摘要：{input}

后续问题：""",
        input_var="input",
    )

    document = """
    2024年3月15日，中国科学院发布了一项重要研究成果。
    该研究由王明教授领导的研究团队完成，主要涉及
    人工智能在气候变化预测中的应用。研究团队使用了
    深度学习模型来分析全球气候数据，并成功预测了未来
    10年的气候变化趋势。这项研究发表在《自然》杂志上。
    """

    return chain.execute(document)


def main():
    print("=" * 60)
    print("链式提示 (Prompt Chaining) 示例")
    print("=" * 60)

    result = document_analysis_example()

    print("\n" + "=" * 60)
    print("执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
