"""
14 - 方向性刺激提示 (DSP)

DSP (Directional Stimulus Prompting) 使用强化学习优化提示词。
核心：学习什么样的"刺激"能引导模型产生更好的回答。

关键组件：
1. 方向性刺激：可以是关键词、策略描述或示例
2. 评估器：评估回答质量
3. 优化器：调整刺激以最大化质量

注意：这是一个简化版，展示 DSP 的核心概念。
真正的 DSP 需要强化学习环境和大量训练。
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


class DirectionalStimulusPrompting:
    def __init__(self):
        self.stimuli = []
        self.scores = []

    def generate_stimulus_candidates(self, task: str, n: int = 3) -> list:
        """生成刺激候选"""
        prompt = f"""为以下任务生成 {n} 个不同的"刺激"提示。

任务是让 AI 完成：{task}

刺激提示应该：
1. 指导 AI 朝正确方向思考
2. 包含有用的策略或提示
3. 简洁明了

输出格式：
1. [刺激提示1]
2. [刺激提示2]
...
{n}. [刺激提示{n}]"""

        result = call_llm(prompt, temperature=0.9)
        if not result["success"]:
            return []

        candidates = []
        for line in result["data"].split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                if "." in line:
                    candidates.append(line.split(".", 1)[1].strip())

        return candidates[:n]

    def evaluate_response(self, response: str, criteria: str) -> float:
        """简单评估回答质量"""
        prompt = f"""评估以下回答的质量。

回答：{response}

评估标准：{criteria}

请给出 0-10 的质量分数，只需输出数字。"""

        result = call_llm(prompt, temperature=0.3)
        if not result["success"]:
            return 5.0

        try:
            score = float(result["data"].strip())
            return min(10.0, max(0.0, score))
        except:
            return 5.0

    def optimize(self, task: str, criteria: str) -> dict:
        """优化方向性刺激"""
        print("=" * 60)
        print("方向性刺激提示 (DSP) 优化")
        print("=" * 60)

        print("\n【步骤1】生成刺激候选...")
        candidates = self.generate_stimulus_candidates(task, n=3)
        print(f"生成了 {len(candidates)} 个候选刺激")

        print("\n【步骤2】评估每个刺激的效果...")
        results = []

        for i, stimulus in enumerate(candidates):
            print(f"\n刺激 {i + 1}: {stimulus}")

            full_prompt = f"{stimulus}\n\n任务：{task}"
            response_result = call_llm(full_prompt)

            if response_result["success"]:
                score = self.evaluate_response(response_result["data"], criteria)
                results.append(
                    {
                        "stimulus": stimulus,
                        "response": response_result["data"],
                        "score": score,
                    }
                )
                print(f"  质量分数: {score:.1f}")

        results.sort(key=lambda x: x["score"], reverse=True)

        print("\n【步骤3】选择最优刺激")
        best = results[0]
        print(f"\n最优刺激（分数: {best['score']:.1f}）：")
        print(f"  {best['stimulus']}")

        return {
            "task": task,
            "criteria": criteria,
            "candidates": candidates,
            "best_stimulus": best["stimulus"],
            "best_score": best["score"],
            "all_results": results,
        }


def main():
    dsp = DirectionalStimulusPrompting()

    task = "解释量子计算的基本原理"
    criteria = "回答应该准确、易懂、有深度"

    result = dsp.optimize(task, criteria)


if __name__ == "__main__":
    main()
