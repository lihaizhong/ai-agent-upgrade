"""
15 - 自我反思 (Reflexion)

自我反思通过语言反馈强化学习，让模型从错误中学习。
核心循环：执行 → 评估 → 反思 → 改进

工作流程：
1. 执行任务，得到结果
2. 评估器判断结果质量
3. 如果失败，反思失败原因
4. 根据反思生成改进策略
5. 重新执行

适用场景：需要从错误中学习的复杂任务
"""

from utils import call_llm


class ReflexionAgent:
    def __init__(self):
        self.memory = []

    def execute(self, task: str) -> dict:
        """执行任务"""
        prompt = f"任务：{task}\n\n请执行任务并给出结果。"
        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def evaluate(self, task: str, response: str, criteria: str) -> dict:
        """评估结果"""
        prompt = f"""评估以下任务执行结果。

任务：{task}
结果：{response}
评估标准：{criteria}

请判断：
1. 任务是否成功完成？
2. 如果失败，原因是什么？
3. 如何改进？

输出格式：
成功/失败：[成功/失败]
原因：[失败原因，如成功则写"无"]
改进建议：[改进建议]"""

        result = call_llm(prompt)
        if not result["success"]:
            return {"success": False, "reason": "评估失败"}

        response_lower = result["data"].lower()
        is_success = "成功" in response_lower and "失败" not in response_lower

        return {
            "success": is_success,
            "evaluation": result["data"],
            "raw_response": response,
        }

    def reflect(self, task: str, failed_response: str, reason: str) -> str:
        """反思失败原因"""
        prompt = f"""任务：{task}
失败结果：{failed_response}
失败原因：{reason}

请深入反思：
1. 为什么会出现这个失败？
2. 问题出在哪个环节？
3. 下次如何避免同样的错误？
4. 有没有更好的解决思路？

反思内容："""

        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def improve(self, task: str, reflection: str) -> str:
        """基于反思生成改进方案"""
        prompt = f"""任务：{task}
反思内容：{reflection}

基于以上反思，请提出一个改进后的任务执行方案。
方案应该：
1. 解决之前失败的问题
2. 使用更有效的策略
3. 包含具体的执行步骤

改进方案："""

        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def run(self, task: str, criteria: str, max_attempts: int = 3) -> dict:
        """运行自我反思循环"""
        print("=" * 60)
        print("自我反思 (Reflexion) 执行")
        print("=" * 60)

        history = []

        for attempt in range(max_attempts):
            print(f"\n【尝试 {attempt + 1}】")
            print("-" * 40)

            if attempt == 0:
                current_task = task
            else:
                current_task = self.improve(task, reflection)
                print(f"改进方案：{current_task[:200]}...")

            response = self.execute(current_task)
            print(f"执行结果：{response[:200]}...")

            eval_result = self.evaluate(task, response, criteria)
            print(f"评估：{'成功' if eval_result['success'] else '失败'}")

            history.append(
                {
                    "attempt": attempt + 1,
                    "task": current_task,
                    "response": response,
                    "evaluation": eval_result,
                }
            )

            if eval_result["success"]:
                print("\n任务成功完成！")
                return {
                    "success": True,
                    "final_response": response,
                    "attempts": attempt + 1,
                    "history": history,
                }

            if attempt < max_attempts - 1:
                reflection = self.reflect(
                    task, response, eval_result.get("reason", "未知")
                )
                print(f"反思：{reflection[:200]}...")

        return {"success": False, "attempts": max_attempts, "history": history}


def main():
    print("=" * 60)
    print("自我反思 (Reflexion) 示例")
    print("=" * 60)

    agent = ReflexionAgent()

    task = "用比喻解释'算法'的概念"
    criteria = "比喻恰当、解释清晰、让人容易理解"

    result = agent.run(task, criteria)

    print(f"\n最终结果：{'成功' if result['success'] else '失败'}")
    print(f"尝试次数：{result['attempts']}")


if __name__ == "__main__":
    main()
