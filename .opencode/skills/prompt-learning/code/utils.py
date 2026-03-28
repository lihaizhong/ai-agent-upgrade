"""
提示词工程代码示例 - 通用工具函数
"""

import os
import time
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    client = None

try:
    from anthropic import Anthropic
except ImportError:
    anthropic = None


def get_openai_client():
    """获取 OpenAI 客户端"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置 OPENAI_API_KEY 环境变量")
    return OpenAI(api_key=api_key)


def get_anthropic_client():
    """获取 Anthropic 客户端"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")
    return Anthropic(api_key=api_key)


def call_openai(
    prompt: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> dict:
    """
    调用 OpenAI LLM

    Args:
        prompt: 用户提示词
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        system_prompt: 系统提示词

    Returns:
        包含 success 和 data/error 的字典
    """
    try:
        client = get_openai_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        elapsed = time.time() - start_time

        return {
            "success": True,
            "data": response.choices[0].message.content,
            "usage": response.usage.total_tokens,
            "elapsed": elapsed,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_anthropic(
    prompt: str,
    model: str = "claude-sonnet-4-20250514",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> dict:
    """
    调用 Anthropic LLM

    Args:
        prompt: 用户提示词
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        system_prompt: 系统提示词

    Returns:
        包含 success 和 data/error 的字典
    """
    try:
        client = get_anthropic_client()

        start_time = time.time()
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed = time.time() - start_time

        return {
            "success": True,
            "data": response.content[0].text,
            "usage": response.usage.input_tokens + response.usage.output_tokens,
            "elapsed": elapsed,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_llm(prompt: str, model: str = "gpt-4o", **kwargs) -> dict:
    """
    统一 LLM 调用接口（自动选择可用客户端）

    支持的模型前缀：
    - gpt-*, claude-* 自动选择对应客户端
    - 默认使用 OpenAI
    """
    if model.startswith("claude-"):
        return call_anthropic(prompt, model=model, **kwargs)
    else:
        return call_openai(prompt, model=model, **kwargs)


def extract_answer(response: str) -> str:
    """
    从 LLM 输出中提取答案
    简单实现：取最后一行或最后一个句子
    """
    lines = response.strip().split("\n")
    if lines:
        # 尝试找"答案："或"最终答案："后面的内容
        for line in reversed(lines):
            if "答案" in line or "answer" in line.lower():
                # 取冒号后面的部分
                if ":" in line:
                    return line.split(":", 1)[1].strip()
        # 没有找到答案标记，返回最后一行
        return lines[-1].strip()
    return response


def vote_most_common(answers: list) -> tuple:
    """
    投票选出最常见的答案

    Args:
        answers: 答案列表

    Returns:
        (最常见答案, 得票数, 总票数)
    """
    from collections import Counter

    counter = Counter(answers)
    most_common = counter.most_common(1)[0]
    return most_common[0], most_common[1], len(answers)


if __name__ == "__main__":
    # 测试调用
    print("测试 LLM 调用...")
    result = call_llm("用一个词回答：天空是什么颜色？")
    if result["success"]:
        print(f"响应：{result['data']}")
    else:
        print(f"错误：{result['error']}")
