"""
05 - 思维树 (Tree of Thoughts, ToT)

思维树通过树状结构系统探索多种可能的解题路径。
核心思想：像下棋一样，提前思考多步，选最佳走法。

实现框架：
1. 生成：产生多个候选思维
2. 评估：判断每个思维的质量
3. 搜索：决定保留哪些，剪掉哪些

搜索策略：
- BFS（广度优先）：保证找到最优解，成本高
- DFS（深度优先）：快速找解，可能非最优
- Beam（集束搜索）：平衡效率和质量
"""

from utils import call_llm
from enum import Enum


class ThoughtState(Enum):
    """思维状态"""

    SURE = "sure"  # 肯定通向正确答案
    MAYBE = "maybe"  # 可能，需要继续探索
    IMPOSSIBLE = "impossible"  # 可以剪枝放弃


def generate_thoughts(problem: str, current_state: str, n_thoughts: int = 3) -> list:
    """生成多个候选思维"""
    prompt = f"""问题：{problem}
当前状态：{current_state}

请生成 {n_thoughts} 个不同的思考方向或步骤。
每个思考方向应该：
1. 是一个具体的行动或推理步骤
2. 与当前状态相关
3. 有明确的下一步

输出格式：
1. [思考方向1]
2. [思考方向2]
3. [思考方向3]"""

    result = call_llm(prompt, temperature=0.8)
    if not result["success"]:
        return []

    thoughts = []
    for line in result["data"].split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            thought = line.split(".", 1)[1].strip() if "." in line else line
            thoughts.append(thought)

    return thoughts[:n_thoughts]


def evaluate_thought(thought: str, problem: str, goal: str) -> dict:
    """评估一个思维的质量"""
    prompt = f"""评估以下思考步骤：

目标：{goal}
问题：{problem}
思考步骤：{thought}

请评估：
1. 这个思考是否正确？
2. 它是否有可能通向正确答案？
3. 是否存在逻辑错误？

请用以下格式回答：
评估：sure/maybe/impossible
理由：[简短解释]"""

    result = call_llm(prompt)
    if not result["success"]:
        return {"state": ThoughtState.MAYBE, "reason": "评估失败"}

    response = result["data"].lower()

    if "sure" in response:
        state = ThoughtState.SURE
    elif "impossible" in response or "错误" in response:
        state = ThoughtState.IMPOSSIBLE
    else:
        state = ThoughtState.MAYBE

    return {"state": state, "reason": result["data"]}


def solve_24_game(numbers: list) -> dict:
    """
    算24游戏 - 思维树的经典示例

    用加减乘除运算使四个数字得到24
    """
    problem = f"用数字 {numbers} 算出24，每个数字只能用一次"
    goal = "找到一种运算组合使结果为24"

    print(f"\n算24游戏：数字 = {numbers}")
    print(f"目标：使用加减乘除运算得到24\n")

    # 简化版：使用专家辩论法
    prompt = f"""假设三位不同的专家来回答这个问题。
所有专家都写下他们思考的第一个步骤，然后分享。
然后继续写下一个步骤并分享。
只要发现有专家出错，就让这位专家离开。
最后给出正确答案。

问题：用数字 {numbers} 算出24"""

    result = call_llm(prompt)
    return result


def creative_writing_planning(topic: str) -> dict:
    """创意写作规划 - 思维树应用"""
    prompt = f"""假设三位不同的专家来回答这个问题。
所有专家都写下他们思考的第一个步骤，然后分享。
然后继续写下一个步骤并分享。
只要发现有专家出错，就让这位专家离开。
最后给出正确答案。

问题：写一篇关于「{topic}」的文章，请规划文章结构和主要内容"""

    result = call_llm(prompt)
    return result


def main():
    print("=" * 60)
    print("思维树 (Tree of Thoughts) 示例")
    print("=" * 60)

    print("\n【示例1】算24游戏")
    print("-" * 40)
    result = solve_24_game([4, 6, 9, 5])
    if result["success"]:
        print(result["data"])

    print("\n【示例2】创意写作规划")
    print("-" * 40)
    result = creative_writing_planning("人工智能对未来工作的影响")
    if result["success"]:
        print(result["data"])


if __name__ == "__main__":
    main()
