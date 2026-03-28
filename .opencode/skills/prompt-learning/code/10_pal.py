"""
10 - 程序辅助语言模型 (PAL)

PAL 让 LLM 生成代码来解决问题，而不是进行自然语言推理。
核心：用代码执行替代复杂的数学/逻辑推理。

适用场景：
- 复杂数学计算
- 需要精确数据处理的问题
- 可以用代码表示的逻辑

注意：需要代码执行环境（如 Python REPL）。
"""

from utils import call_llm


def execute_python(code: str) -> dict:
    """执行 Python 代码并返回结果"""
    try:
        import io
        import contextlib

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exec(code)

        return {"success": True, "output": stdout.getvalue()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def pal_solve(problem: str) -> dict:
    """PAL 解决问题"""
    prompt = f"""请为以下问题生成 Python 代码来解答。
直接输出代码，不要解释。代码应该：
1. 定义清晰的变量
2. 包含必要的计算步骤
3. 最后打印答案

问题：{problem}

代码："""

    result = call_llm(prompt, temperature=0.3)
    if not result["success"]:
        return result

    code = result["data"]
    print(f"生成的代码：\n{code}")
    print("\n执行结果：")

    exec_result = execute_python(code)

    return {"success": True, "generated_code": code, "execution_result": exec_result}


def compare_cot_vs_pal(problem: str):
    """对比思维链和 PAL 的效果"""
    print("=" * 60)
    print("对比：思维链 vs PAL")
    print("=" * 60)

    # 思维链
    print("\n【思维链解答】")
    print("-" * 40)
    cot_prompt = f"{problem}\n\n让我们一步步思考。"
    cot_result = call_llm(cot_prompt)
    if cot_result["success"]:
        print(cot_result["data"])

    # PAL
    print("\n【PAL 解答】")
    print("-" * 40)
    pal_result = pal_solve(problem)
    if pal_result["success"]:
        print(pal_result["execution_result"])


def main():
    print("=" * 60)
    print("程序辅助语言模型 (PAL) 示例")
    print("=" * 60)

    problems = [
        "一个水池有进水管和出水管。单独开进水管8小时注满，单独开出水管12小时放完。现在两管同时打开，需要多少小时注满？",
        "某人投资10000元，年利率5%，按复利计算，10年后有多少钱？",
    ]

    for problem in problems:
        compare_cot_vs_pal(problem)
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
