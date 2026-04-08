"""
03 - 思维链提示 (Chain-of-Thought Prompting)

思维链提示引导模型展示推理过程，提高复杂问题的准确性。
核心：在答案前加入"让我们一步步思考"触发推理步骤。

两种方式：
1. 零样本思维链：只需添加触发语
2. 少样本思维链：在示例中展示推理过程

适用场景：数学推理、逻辑分析、多步决策
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


def zero_shot_cot():
    """零样本思维链 - 最简单的方式"""
    prompt = """小明有10个苹果，给了邻居2个，给了修理工2个，
然后又买了5个，吃了1个。还剩多少苹果？

让我们一步步思考。"""

    result = call_llm(prompt)
    return result


def few_shot_cot():
    """少样本思维链 - 在示例中展示推理"""
    prompt = """问题：奇数之和是否为偶数？数字：4, 8, 9, 15, 12, 2, 1
推理：奇数有9, 15, 1，共3个。3个奇数相加，和为奇数。
答案：False

问题：奇数之和是否为偶数？数字：15, 32, 5, 13, 82, 7, 1
推理："""

    result = call_llm(prompt)
    return result


def math_reasoning():
    """数学推理示例"""
    prompt = """计算以下问题，展示完整推理过程：

问题：一个水池有进水和出水两根水管。单独开进水管8小时可以注满，
单独开水管10小时可以放完。现在同时打开两根水管，需要多少小时注满？

让我们一步步分析。"""

    result = call_llm(prompt)
    return result


def logical_reasoning():
    """逻辑推理示例"""
    prompt = """分析以下逻辑问题：

前提：
1. 所有程序员都写代码
2. 有些程序员使用Python
3. 小王是程序员

结论：小王一定写代码吗？

让我们一步步推导。"""

    result = call_llm(prompt)
    return result


def main():
    print("=" * 60)
    print("思维链提示 (Chain-of-Thought Prompting) 示例")
    print("=" * 60)

    print("\n【示例1】零样本思维链 - 苹果问题")
    print("-" * 40)
    result = zero_shot_cot()
    if result["success"]:
        print(result["data"])

    print("\n【示例2】少样本思维链 - 奇偶判断")
    print("-" * 40)
    result = few_shot_cot()
    if result["success"]:
        print(result["data"])

    print("\n【示例3】数学推理 - 水池问题")
    print("-" * 40)
    result = math_reasoning()
    if result["success"]:
        print(result["data"])

    print("\n【示例4】逻辑推理")
    print("-" * 40)
    result = logical_reasoning()
    if result["success"]:
        print(result["data"])


if __name__ == "__main__":
    main()
