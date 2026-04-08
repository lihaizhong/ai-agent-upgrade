"""
11 - 自动推理和工具使用 (ART)

ART (Automatic Reasoning and Tool-use) 让模型自动选择和使用工具。
核心：从任务示例库中自动选择合适的工具组合。

工作流程：
1. 给定新任务
2. 从库中检索相关工具示例
3. 自动组合工具解决问题

注意：这是一个简化框架，展示核心逻辑。
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


class Tool:
    def __init__(self, name: str, description: str, example: str):
        self.name = name
        self.description = description
        self.example = example

    def use(self, input_text: str) -> str:
        return f"[{self.name}] 执行结果: {input_text}"


class ART:
    def __init__(self):
        self.tools = []
        self.tool_registry = {}
        self._init_tools()

    def _init_tools(self):
        tools_data = [
            ("search", "搜索信息", "search('关键词')"),
            ("calculate", "执行计算", "calculate('表达式')"),
            ("lookup", "查询事实", "lookup('实体')"),
            ("translate", "翻译文本", "translate('文本', '目标语言')"),
            ("summarize", "总结内容", "summarize('文本')"),
        ]

        for name, desc, example in tools_data:
            tool = Tool(name, desc, example)
            self.tools.append(tool)
            self.tool_registry[name] = tool

    def retrieve_tools(self, task: str, top_k: int = 2) -> list:
        """根据任务检索相关工具"""
        prompt = f"""分析以下任务，判断需要哪些工具来完成任务。

任务：{task}

可用工具：
{chr(10).join([f"- {t.name}: {t.description}" for t in self.tools])}

请选择最相关的 {top_k} 个工具，并说明为什么选择它们。

输出格式：
工具1: [工具名]
理由: [选择理由]
工具2: [工具名]
理由: [选择理由]"""

        result = call_llm(prompt)
        if not result["success"]:
            return []

        response = result["data"]
        selected = []
        for tool in self.tools:
            if tool.name in response.lower():
                selected.append(tool)

        return selected[:top_k]

    def solve(self, task: str) -> dict:
        """使用 ART 解决任务"""
        print(f"任务：{task}\n")

        # 步骤1：检索相关工具
        print("步骤1：检索相关工具...")
        selected_tools = self.retrieve_tools(task)
        print(f"选择工具：{[t.name for t in selected_tools]}\n")

        # 步骤2：制定使用计划
        print("步骤2：制定解决计划...")
        plan_prompt = f"""任务：{task}
已选择工具：{[t.name for t in selected_tools]}

请制定解决这个任务的步骤计划，说明每一步使用哪个工具。"""

        plan_result = call_llm(plan_prompt)
        if not plan_result["success"]:
            return {"success": False, "error": "无法制定计划"}

        print(f"计划：\n{plan_result['data']}\n")

        # 步骤3：执行计划（简化版）
        print("步骤3：执行计划...")
        exec_prompt = f"""任务：{task}
解决计划：{plan_result["data"]}

请执行计划，直接给出最终答案。"""

        exec_result = call_llm(exec_prompt)

        return {
            "success": exec_result["success"],
            "task": task,
            "selected_tools": [t.name for t in selected_tools],
            "plan": plan_result["data"],
            "solution": exec_result["data"]
            if exec_result["success"]
            else exec_result["error"],
        }


def main():
    print("=" * 60)
    print("自动推理和工具使用 (ART) 示例")
    print("=" * 60)

    art = ART()

    tasks = [
        "搜索2024年奥运会的举办城市，并计算与中国时差",
        "查找量子计算的基本原理，并用中文总结",
    ]

    for task in tasks:
        print(f"\n{'=' * 60}")
        result = art.solve(task)
        if result["success"]:
            print(f"\n最终答案：\n{result['solution']}")


if __name__ == "__main__":
    main()
