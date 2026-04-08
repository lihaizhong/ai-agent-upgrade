"""
01 - 零样本提示 (Zero-Shot Prompting)

零样本提示是最基础的提示词技术，直接给出任务指令，不提供示例。
这是初学者入门的必修课。

核心概念：
- 不提供任何示例
- 直接描述任务和要求
- 依赖模型的预训练知识

适用场景：
- 简单明确的任务
- 模型熟悉领域
- 快速原型开发
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


def basic_zero_shot():
    """最基本的零样本提示"""
    prompt = """请将以下中文翻译成英文：
今天天气真好！"""

    result = call_llm(prompt)
    return result


def zero_shot_with_constraints():
    """带约束条件的零样本提示"""
    prompt = """你是一个技术文档翻译专家。
请将以下技术文档从中文翻译成英文。
要求：
1. 保持专业术语的准确性
2. 符合英文技术文档的表达习惯
3. 长度与原文相近

原文：
大语言模型通过海量文本数据进行训练，学习语言的统计规律和语义表示。"""

    result = call_llm(prompt)
    return result


def zero_shot_structured_output():
    """要求结构化输出的零样本提示"""
    prompt = """分析以下产品评论，按指定格式输出情感分析结果。

评论："这个手机拍照效果很棒，但是电池续航太差了，一天要充两次电。"

输出格式（JSON）：
{
    "sentiment": "positive/negative/neutral",
    "positive_aspects": ["..."],
    "negative_aspects": ["..."],
    "summary": "一句话总结"
}"""

    result = call_llm(prompt)
    return result


def main():
    print("=" * 60)
    print("零样本提示 (Zero-Shot Prompting) 示例")
    print("=" * 60)

    print("\n【示例1】基本零样本提示")
    print("-" * 40)
    result = basic_zero_shot()
    if result["success"]:
        print(f"问题：今天天气真好！翻译成英文？")
        print(f"回答：{result['data']}")
    else:
        print(f"错误：{result['error']}")

    print("\n【示例2】带约束条件的零样本提示")
    print("-" * 40)
    result = zero_shot_with_constraints()
    if result["success"]:
        print(f"回答：{result['data']}")
    else:
        print(f"错误：{result['error']}")

    print("\n【示例3】要求结构化输出的零样本提示")
    print("-" * 40)
    result = zero_shot_structured_output()
    if result["success"]:
        print(f"回答：{result['data']}")
    else:
        print(f"错误：{result['error']}")


if __name__ == "__main__":
    main()
