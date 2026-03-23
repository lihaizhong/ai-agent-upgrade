# DeepAgent 实战学习计划

> **目标**：通过修改 `build-data-analysis-agent` 项目，掌握 DeepAgent 核心概念，无需阅读冗长文档。

## 前置准备

确保已配置好环境：

```bash
# 1. 安装依赖（在项目根目录）
cd ~/ai-agent-upgrade
uv sync

# 2. 配置环境变量（项目根目录的 .env 文件）
# 已包含：ANTHROPIC_API_KEY, OPENAI_API_KEY, LANGSMITH_API_KEY 等
```

## 核心概念速览

DeepAgent 的核心代码只有这一行：

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-5-latest",
    tools=[...],           # Agent 能用的工具
    backend=backend,       # 代码执行环境
    checkpointer=...,      # 记忆/状态管理
    system_prompt="..."    # 角色设定
)
```

然后运行：

```python
for step in agent.stream({"messages": [...]}, config):
    # 观察 Agent 的思考过程
    print(step)
```

**仅此而已**。其余都是围绕这 5 个参数的扩展。

---

## 阶段一：理解 Agent 循环（第 1-2 天）

### 目标
理解 Agent 如何工作：调用 LLM → 决定工具 → 执行 → 循环直到完成。

### 实践

**1. 运行示例项目**

```bash
cd practice/build-data-analysis-agent
python main.py
```

观察输出，注意：
- Agent 如何接收任务（分析 CSV 文件）
- 它调用了哪些工具（读取文件、执行代码等）
- 如何逐步生成分析结果

**2. 修改 System Prompt**

编辑 `main.py` 第 149-165 行的 `system_prompt`，让 Agent：
- 用中文诗人风格回答（"请用李白式的豪放风格描述数据趋势"）
- 添加特定的分析要求（"必须计算同比增长率"）
- 改变输出格式（"用 Markdown 表格展示结果"）

```python
system_prompt="""你是一个专业的数据分析助手...
【在这里添加你的新要求】
"""
```

**3. 简化任务**

将第 216-224 行的复杂查询改为简单查询：

```python
query = "读取 /home/daytona/data/sales_data.csv 文件，告诉我有多少行数据"
```

观察 Agent 如何用最少的步骤完成任务。

### 检查点
- [ ] 成功运行项目并看到分析结果
- [ ] 能解释 Agent 循环的基本流程
- [ ] 知道如何通过修改 system_prompt 改变 Agent 行为

---

## 阶段二：工具系统（第 3-5 天）

### 目标
理解如何扩展 Agent 能力：添加自定义工具。

### 实践

**1. 分析现有工具**

查看 `main.py` 中的 `slack_send_message` 工具（第 72-102 行）：

```python
@tool(parse_docstring=True)
def slack_send_message(text: str, file_path: Optional[str] = None) -> str:
    """发送消息到 Slack，可选附带文件。
    Args:
        text: 消息文本内容
        file_path: 要上传的文件路径（可选）
    """
    # 实现逻辑...
```

关键要素：
- `@tool` 装饰器：标记为 Agent 可用工具
- 函数 docstring：LLM 通过它理解工具用途
- 类型注解：定义参数类型

**2. 添加新工具**

在 `slack_send_message` 后添加一个新工具：

```python
import datetime

@tool(parse_docstring=True)
def get_current_time() -> str:
    """获取当前时间。
    
    当用户询问时间、日期或需要基于当前时间的计算时使用此工具。
    """
    now = datetime.datetime.now()
    return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
```

然后在第 213 行将工具添加到列表：

```python
tools = [slack_send_message, get_current_time]
```

**3. 测试新工具**

修改查询，让它使用时间工具：

```python
query = "读取 CSV 文件，告诉我当前时间，并分析数据中哪个产品最畅销"
```

观察 Agent 是否在合适的时机调用了 `get_current_time`。

**4. 添加数据处理工具**

创建一个更有用的工具：

```python
@tool(parse_docstring=True)
def calculate_statistics(numbers: list[float]) -> str:
    """计算一组数字的基本统计信息。
    
    Args:
        numbers: 数字列表，如 [10, 20, 30, 40]
        
    Returns:
        包含平均值、中位数、最大最小值的字符串
    """
    import statistics
    avg = statistics.mean(numbers)
    median = statistics.median(numbers)
    return f"平均值: {avg:.2f}, 中位数: {median:.2f}, 最大值: {max(numbers)}, 最小值: {min(numbers)}"
```

### 检查点
- [ ] 成功添加并测试至少 2 个新工具
- [ ] 能解释 `@tool` 装饰器和 docstring 的作用
- [ ] 理解为什么 LLM 能"智能"选择工具（基于描述）

---

## 阶段三：后端与沙箱（第 6-7 天）

### 目标
理解代码执行环境：Daytona 沙箱 vs 本地后端。

### 实践

**1. 对比两种后端**

查看 `main.py` 第 105-132 行的后端创建逻辑：

```python
def create_daytona_backend():
    """创建 Daytona 沙箱后端。"""
    from daytona import Daytona
    from langchain_daytona import DaytonaSandbox
    # ... 创建隔离的沙箱环境

def create_local_backend():
    """创建本地 Shell 后端（用于开发测试）。"""
    from deepagents.backends import LocalShellBackend
    # ... 使用本地环境
```

**2. 强制使用本地后端**

临时修改代码，跳过 Daytona 尝试：

```python
def create_daytona_backend():
    """创建 Daytona 沙箱后端。"""
    # 直接返回本地后端，不尝试 Daytona
    return create_local_backend()
```

运行观察：Agent 是否能在本地环境正常工作？

**3. 理解沙箱的价值**

思考：
- 为什么需要 Daytona 沙箱？
- 什么情况下本地后端就够了？
- Agent 执行代码时，沙箱提供了什么保护？

### 检查点
- [ ] 理解 Daytona 沙箱和本地后端的区别
- [ ] 知道何时使用哪种后端
- [ ] 理解沙箱在安全性上的作用

---

## 阶段四：记忆与多轮对话（第 8-10 天）

### 目标
理解 `checkpointer` 和 `thread_id` 如何实现多轮对话。

### 实践

**1. 分析记忆机制**

查看 `main.py` 相关代码：

```python
from langgraph.checkpoint.memory import InMemorySaver

# 创建检查点器（记忆管理器）
checkpointer = InMemorySaver()

# 创建 Agent 时传入
create_deep_agent(..., checkpointer=checkpointer)

# 运行时指定线程 ID
config = {"configurable": {"thread_id": thread_id}}
```

**2. 测试多轮对话**

项目已支持多轮对话（第 232-238 行）。运行后输入：

```
第一轮：分析 CSV 文件并生成报告
第二轮：刚才分析的是什么数据？（测试记忆）
第三轮：详细分析 Widget A 的销售趋势（基于上下文）
```

**3. 实现对话重置**

添加功能：输入 "reset" 时重置对话（生成新的 thread_id）：

```python
if user_input.lower() == "reset":
    thread_id = str(uuid.uuid4())
    print(f"🔄 已重置对话，新线程 ID: {thread_id}")
    continue
```

**4. 持久化记忆（进阶）**

`InMemorySaver` 只是内存存储，程序退出记忆消失。尝试改用文件存储：

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 使用 SQLite 持久化记忆
checkpointer = SqliteSaver.from_conn_string("checkpoints.sqlite")
```

### 检查点
- [ ] 理解 thread_id 的作用
- [ ] 能解释 checkpointer 的工作原理
- [ ] 知道内存存储和持久化存储的区别

---

## 阶段五：数据分析实战（第 11-14 天）

### 目标
综合运用所学，完成完整的数据分析任务。

### 实践

**1. 使用真实数据**

替换示例数据（第 41-55 行的 `create_sample_data`）：读取你自己的 CSV 文件：

```python
def create_sample_data():
    """加载真实数据。"""
    import pandas as pd
    df = pd.read_csv("~/Documents/my_data.csv")
    return df.values.tolist()
```

或者修改 `upload_data_to_backend` 直接上传本地文件。

**2. 定制分析流程**

修改查询（第 216-224 行），要求 Agent：
- 清洗数据（处理缺失值）
- 生成特定类型的图表
- 计算自定义指标
- 导出到指定格式

**3. 添加报告生成工具**

创建一个生成 PDF/HTML 报告的工具：

```python
@tool(parse_docstring=True)
def generate_report(content: str, filename: str) -> str:
    """生成 Markdown 格式的分析报告并保存。
    
    Args:
        content: 报告内容
        filename: 保存的文件名（不含扩展名）
    """
    report_path = f"/home/daytona/{filename}.md"
    with open(report_path, 'w') as f:
        f.write(f"# 数据分析报告\\n\\n")
        f.write(f"生成时间: {datetime.datetime.now()}\\n\\n")
        f.write(content)
    return f"报告已保存至: {report_path}"
```

**4. 自动化任务**

创建一个脚本，让 Agent 自动执行预设的分析任务，无需交互：

```python
def run_batch_analysis():
    """批量分析多个文件。"""
    files = ["data1.csv", "data2.csv", "data3.csv"]
    for file in files:
        query = f"分析 {file} 并生成摘要"
        run_analysis(agent, query)
```

### 检查点
- [ ] 成功分析自己的数据
- [ ] 生成自定义格式的报告
- [ ] 理解如何将 Agent 集成到工作流

---

## 阶段六：项目扩展（第 15-21 天）

### 选择一项进行实战

### 选项 A：智能数据管道

**目标**：自动监控数据目录，新文件到达时自动分析。

**实现思路**：
1. 添加 `watch_directory` 工具监控文件夹
2. 新文件到达时触发分析
3. 将结果发送到 Slack/邮件
4. 使用 `InMemorySaver` 跟踪已处理文件

### 选项 B：对话式数据助手

**目标**：构建类 ChatGPT 的数据分析助手。

**实现思路**：
1. 创建一个 Web 界面（用 Gradio/Streamlit）
2. 每条用户消息调用 `agent.stream()`
3. 显示 Agent 的思考过程（工具调用）
4. 保留对话历史（使用 SQLiteSaver）

### 选项 C：专项分析 Agent

**目标**：针对特定领域的专业分析。

**示例**：
- **财务分析 Agent**：专注于财报分析，内置财务指标计算工具
- **SEO 分析 Agent**：分析网站流量数据，提供优化建议
- **运维分析 Agent**：分析日志文件，检测异常模式

**实现步骤**：
1. 设计领域特定的 tools（5-10 个）
2. 编写专业的 system_prompt
3. 准备示例数据测试
4. 封装为可复用的类

---

## 参考：核心 API

### create_deep_agent 参数

```python
create_deep_agent(
    model: str,              # 模型，如 "anthropic:claude-sonnet-4-5-latest"
    tools: list,            # 工具列表，用 @tool 装饰的函数
    backend: Backend,       # 执行后端（Daytona/LocalShell）
    checkpointer: Saver,    # 记忆管理器（InMemorySaver/SqliteSaver）
    system_prompt: str,     # 系统提示词，定义 Agent 角色和能力
)
```

### 常用工具模式

```python
from langchain.tools import tool

@tool(parse_docstring=True)
def my_tool(param1: str, param2: int = 10) -> str:
    """工具描述，LLM 通过它理解何时使用此工具。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述，默认为 10
    """
    # 实现逻辑
    return "结果"
```

### 流式输出

```python
for step in agent.stream({
    "messages": [{"role": "user", "content": "查询"}]
}, config, stream_mode="updates"):
    # step 包含 Agent 的思考过程和工具调用
    print(step)
```

---

## 学习资源

### 必读（5分钟）
- `practice/build-data-analysis-agent/main.py` - 完整的 DeepAgent 示例
- 本文档 - 实战路径指南

### 参考（按需查阅）
- DeepAgent 源码中的 docstring
- `langchain` 和 `langgraph` 的基础概念

### 无需阅读
- ❌ DeepAgent 官方长篇文档
- ❌ LangChain 完整教程
- ❌ 各种理论文章

---

## 检查清单

完成学习后，你应该能够：

- [ ] 独立创建 DeepAgent 项目
- [ ] 添加自定义工具扩展功能
- [ ] 配置不同的后端环境
- [ ] 实现多轮对话和记忆
- [ ] 将 Agent 集成到实际工作流
- [ ] 向他人解释 DeepAgent 的核心机制

---

## 快速启动

立即开始：

```bash
# 1. 运行示例
cd practice/build-data-analysis-agent
python main.py

# 2. 修改 system_prompt，观察行为变化
vim main.py  # 编辑第 149-165 行

# 3. 添加你的第一个工具
# 在 slack_send_message 函数后添加新工具

# 4. 重新运行测试
python main.py
```

**记住**：最好的学习方式是动手改代码，而不是阅读文档。
