"""
LangChain DeepAgent 数据分析 Agent

本项目演示如何使用 LangChain DeepAgent 构建一个智能数据分析 Agent，能够：
- 读取和分析 CSV 数据
- 生成可视化图表
- 执行统计分析
- 生成分析报告

核心组件：
- DeepAgent: LangChain 高级 Agent 框架
- Daytona: 沙箱环境用于安全执行代码
- Pandas/Matplotlib: 数据处理和可视化
"""

import csv
import io
import os

# 从项目根目录加载 .env 文件
import pathlib
import uuid
from typing import Optional

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

project_root = pathlib.Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=project_root / ".env", verbose=True)


def setup_environment():
    """设置环境变量。"""
    os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "")
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


def create_sample_data():
    """创建示例销售数据。"""
    return [
        ["Date", "Product", "Units Sold", "Revenue"],
        ["2025-08-01", "Widget A", 10, 250],
        ["2025-08-02", "Widget B", 5, 125],
        ["2025-08-03", "Widget A", 7, 175],
        ["2025-08-04", "Widget C", 3, 90],
        ["2025-08-05", "Widget B", 8, 200],
        ["2025-08-06", "Widget A", 12, 300],
        ["2025-08-07", "Widget C", 4, 120],
        ["2025-08-08", "Widget B", 6, 150],
        ["2025-08-09", "Widget A", 9, 225],
        ["2025-08-10", "Widget C", 5, 150],
    ]


def upload_data_to_backend(
    backend, data: list, file_path: str = "/home/daytona/data/sales_data.csv"
):
    """将数据上传到后端沙箱。"""
    text_buf = io.StringIO()
    writer = csv.writer(text_buf)
    writer.writerows(data)
    csv_bytes = text_buf.getvalue().encode("utf-8")
    text_buf.close()

    backend.upload_files([(file_path, csv_bytes)])
    print(f"✅ 数据已上传到: {file_path}")


@tool(parse_docstring=True)
def slack_send_message(text: str, file_path: Optional[str] = None) -> str:
    """发送消息到 Slack，可选附带文件。

    Args:
        text: 消息文本内容
        file_path: 要上传的文件路径（可选）
    """
    try:
        from slack_sdk import WebClient

        slack_token = os.environ.get("SLACK_BOT_TOKEN")
        channel_id = os.environ.get("SLACK_CHANNEL_ID")

        if not slack_token or not channel_id:
            return (
                "⚠️ Slack 配置未设置，请检查环境变量 SLACK_BOT_TOKEN 和 SLACK_CHANNEL_ID"
            )

        client = WebClient(token=slack_token)

        if not file_path:
            client.chat_postMessage(channel=channel_id, text=text)
        else:
            client.files_upload_v2(
                channel=channel_id,
                file=file_path,
                initial_comment=text,
            )

        return "✅ 消息已发送到 Slack"
    except Exception as e:
        return f"❌ 发送失败: {str(e)}"


@tool(parse_docstring=True)
def get_current_time() -> str:
    """获取当前时间。

    当用户询问时间、日期或需要基于当前时间的计算时使用此工具。
    """
    import datetime

    now = datetime.datetime.now()
    return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool(parse_docstring=True)
def calculate_statistics(numbers: list[float]) -> str:
    """计算一组数字的基本统计信息。

    Args:
        numbers: 数字列表，如 [10, 20, 30, 40]

    Returns:
        包含平均值、中位数、最大最小值的字符串
    """
    import statistics

    if not numbers:
        return "错误：数字列表为空"
    avg = statistics.mean(numbers)
    median = statistics.median(numbers)
    return f"平均值: {avg:.2f}, 中位数: {median:.2f}, 最大值: {max(numbers)}, 最小值: {min(numbers)}"


def create_daytona_backend():
    """创建 Daytona 沙箱后端。"""
    try:
        from daytona import Daytona
        from langchain_daytona import DaytonaSandbox

        print("🚀 正在创建 Daytona 沙箱...")
        daytona = Daytona()
        sandbox = daytona.create()
        backend = DaytonaSandbox(sandbox=sandbox)

        result = backend.execute("echo '沙箱就绪'")
        print(f"✅ {result.output}")

        return backend
    except Exception as e:
        print(f"❌ Daytona 初始化失败: {e}")
        print("💡 尝试使用本地 Shell 后端...")
        return create_local_backend()


def create_local_backend():
    """创建本地 Shell 后端（用于开发测试）。"""
    from deepagents.backends import LocalShellBackend

    print("⚠️ 使用本地 Shell 后端（仅用于开发测试）")
    backend = LocalShellBackend(
        root_dir=".", env={"PATH": "/usr/bin:/bin:/usr/local/bin"}
    )
    return backend


def create_data_analysis_agent(backend, tools=None):
    """创建数据分析 Agent。"""
    from deepagents import create_deep_agent

    print("🤖 正在创建 Deep Agent...")

    all_tools = tools or []
    checkpointer = InMemorySaver()

    # 从环境变量读取模型配置
    # 注意：OPENAI_MODEL_ID 如果包含 "openai:" 前缀，需要去掉
    # 因为 ChatOpenAI(model="openai:gpt-5.4") 会失败，前缀只在字符串格式时需要
    model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4o")
    if model_id.startswith("openai:"):
        model_id = model_id[len("openai:") :]  # 去掉 "openai:" 前缀

    api_key = os.getenv("OPENAI_API_KEY", "")
    api_base = os.getenv(
        "OPENAI_API_BASE"
    )  # 不设置默认值，None 时 ChatOpenAI 会用默认地址

    from pydantic import SecretStr

    model = ChatOpenAI(
        model_name=model_id,
        openai_api_key=SecretStr(api_key) if api_key else None,
        openai_api_base=api_base,
    )

    agent = create_deep_agent(
        model=model,
        tools=all_tools,
        backend=backend,
        checkpointer=checkpointer,
        system_prompt="""你是一个专业的数据分析助手，风格如李白般豪放飘逸。你的任务是：
1. 读取和分析 CSV 数据文件
2. 进行探索性数据分析（EDA）
3. 生成可视化图表
4. 提供数据洞察和建议

【风格要求】
- 回答如同李白作诗，意境开阔，豪情万丈
- 分析结论要有诗意，如" Widget A 如同长风破浪，独占鳌头"
- 使用"吾观此数据"、"妙哉"等古风词汇

【分析要求】
- 必须计算同比增长率
- 用 Markdown 表格展示结果
- 图表保存为 PNG 格式

执行分析时：
- 使用 pandas 进行数据处理
- 使用 matplotlib/seaborn 生成图表
- 将图表保存到 /home/daytona/ 目录（如果使用 Daytona）

你可以使用以下工具：
- 文件系统工具（ls, read_file, write_file）
- Python 代码执行
- Slack 发送消息（如果已配置）
""",
    )

    print("✅ Agent 创建成功")
    return agent


def run_analysis(agent, query: str, thread_id: Optional[str] = None):
    """运行数据分析任务。"""
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    input_message = {
        "role": "user",
        "content": query,
    }

    print(f"\n📝 用户查询: {query}")
    print("=" * 60)

    for step in agent.stream(
        {"messages": [input_message]},
        config,
        stream_mode="updates",
    ):
        for node_name, update in step.items():
            if (
                update
                and (messages := update.get("messages"))
                and isinstance(messages, list)
            ):
                for message in messages:
                    message.pretty_print()

    return thread_id


def main():
    """主函数。"""
    print("=" * 60)
    print("🚀 LangChain DeepAgent Data Analysis Agent")
    print("=" * 60)

    setup_environment()

    backend = create_daytona_backend()

    sample_data = create_sample_data()
    upload_data_to_backend(backend, sample_data)

    tools = [slack_send_message, get_current_time, calculate_statistics]
    agent = create_data_analysis_agent(backend, tools=tools)

    query = (
        "分析 /home/daytona/data/sales_data.csv 文件，生成一份完整的数据分析报告。"
        "包括：\n"
        "1. 数据概览和基本统计\n"
        "2. 产品销售趋势分析\n"
        "3. 生成可视化图表\n"
        "4. 提供业务洞察和建议\n"
        "将分析结果保存到 /home/daytona/analysis_report.txt，图表保存为 PNG 格式。"
    )

    thread_id = run_analysis(agent, query)

    print("\n" + "=" * 60)
    print(f"✅ 分析完成！线程 ID: {thread_id}")
    print("=" * 60)

    while True:
        user_input = input("\n💬 输入后续问题（或输入 'exit' 退出）: ").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("👋 再见！")
            break

        run_analysis(agent, user_input, thread_id=thread_id)


if __name__ == "__main__":
    main()
