# 🤖 LangChain DeepAgent 数据分析 Agent

使用 LangChain DeepAgent 构建的智能数据分析 Agent，能够自动分析 CSV 数据、生成可视化图表并提供业务洞察。

## ✨ 功能特性

- 📊 **数据读取与处理**：自动读取 CSV 文件，进行数据清洗和预处理
- 📈 **探索性数据分析 (EDA)**：生成统计摘要、趋势分析
- 🎨 **可视化图表**：使用 Matplotlib/Seaborn 生成专业图表
- 🧠 **智能洞察**：基于数据自动生成业务建议
- 💬 **多轮对话**：支持连续追问和深入分析
- 🔒 **安全执行**：使用 Daytona 沙箱隔离执行环境

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Deep Data Analysis Agent                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Backend │   │  Tools   │   │  Model   │   │  Memory  │
   │ (Daytona│   │(File I/O,│   │(Claude/  │   │(InMemory │
   │ Sandbox)│   │ Slack)   │   │ GPT)     │   │ Saver)   │
   └─────────┘   └──────────┘   └──────────┘   └──────────┘
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 `uv`（Python 包管理器）：

```bash
# 安装 uv (如果还没有)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装依赖

项目使用根目录的 `pyproject.toml` 统一管理依赖：

```bash
# 在项目根目录安装依赖（假设项目位于 ~/ai-agent-upgrade）
cd ~/ai-agent-upgrade
uv sync
```

### 3. 配置环境变量

项目使用根目录的 `.env` 文件。请确保已在项目根目录配置好环境变量：

```bash
# 项目根目录的 .env 文件（假设项目位于 ~/ai-agent-upgrade）
~/ai-agent-upgrade/.env
```

必需的环境变量：
- `ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY` - LLM API Key
- `DAYTONA_API_KEY` - Daytona 沙箱 API Key（可选，会回退到本地 Shell）
- `LANGSMITH_API_KEY` - LangSmith 追踪（可选但推荐）

### 4. 运行 Agent

```bash
# 切换到项目目录（假设项目位于 ~/ai-agent-upgrade）
cd ~/ai-agent-upgrade/practice/build-data-analysis-agent

# 使用 uv 运行（自动使用根目录的虚拟环境）
uv run python main.py

# 或者激活虚拟环境后运行
cd ~/ai-agent-upgrade
source .venv/bin/activate
cd practice/build-data-analysis-agent
python main.py
```

## 📋 使用示例

### 基础分析

```python
# 分析销售数据
query = "分析 sales_data.csv，生成数据概览和可视化图表"
agent.invoke({"messages": [{"role": "user", "content": query}]})
```

### 高级分析

```python
# 深度分析
query = """
分析销售数据并回答：
1. 哪款产品表现最好？
2. 销售趋势如何？
3. 有什么异常值？
4. 给出提升销售的建议
"""
```

### 多轮对话

Agent 支持多轮对话，可以连续追问：

```
💬 输入后续问题（或输入 'exit' 退出）: 详细分析 Widget A 的销售趋势
💬 输入后续问题（或输入 'exit' 退出）: 对比三个产品的增长率
```

## 📁 项目结构

```
build-data-analysis-agent/
├── data/
│   └── sample_sales.csv      # 示例数据
├── main.py                   # 主程序
└── README.md                 # 本文档

依赖和环境变量使用项目根目录的配置（假设项目位于 ~/ai-agent-upgrade）：
- ~/ai-agent-upgrade/pyproject.toml  # 项目依赖
- ~/ai-agent-upgrade/.env           # 环境变量
```

## 🔧 核心组件说明

### 1. DeepAgent (`create_deep_agent`)

核心 Agent 创建函数，配置：
- **Model**: LLM 模型（Claude Sonnet 4.5 / GPT-4）
- **Tools**: 可用工具集
- **Backend**: 代码执行后端
- **Checkpointer**: 状态持久化

### 2. Backend (Daytona Sandbox)

提供隔离的执行环境：
- 安全执行 Python 代码
- 文件系统操作
- 数据持久化

备选后端：
- `LocalShellBackend` - 本地开发测试
- `ModalSandbox` - Modal 云服务
- `RunloopSandbox` - Runloop 沙箱

### 3. Tools

内置工具：
- `ls` - 列出目录
- `read_file` - 读取文件
- `write_file` - 写入文件
- `execute` - 执行命令

自定义工具：
- `slack_send_message` - 发送 Slack 消息

### 4. Memory (Checkpointer)

使用 `InMemorySaver` 实现：
- 多轮对话上下文保持
- 线程隔离
- 状态恢复

## 🎯 学习要点

### 1. Deep Agents 核心概念

| 概念 | 说明 | 用途 |
|------|------|------|
| Planning | 任务规划 | Agent 自动分解复杂任务 |
| Context Management | 上下文管理 | 使用文件系统管理大量上下文 |
| Subagents | 子代理 | 派生子代理处理特定子任务 |
| Backends | 后端 | 可插拔的文件系统后端 |

### 2. 代码执行流程

```
User Query
    ↓
Agent Planning (分解任务)
    ↓
Execute Code in Backend (Daytona)
    ↓
Generate Visualizations (Matplotlib)
    ↓
Return Results
```

### 3. 最佳实践

- ✅ 使用沙箱后端确保代码执行安全
- ✅ 配置 LangSmith 追踪 Agent 行为
- ✅ 设计清晰的 System Prompt 指导 Agent
- ✅ 使用类型注解定义 Tool 参数
- ✅ 处理错误和异常情况

## 🛠️ 扩展开发

### 添加自定义工具

```python
from langchain.tools import tool

@tool(parse_docstring=True)
def my_custom_tool(param: str) -> str:
    """工具描述。
    
    Args:
        param: 参数说明
    """
    # 实现逻辑
    return "结果"

# 添加到 Agent
tools = [my_custom_tool]
agent = create_deep_agent(tools=tools, ...)
```

### 集成其他数据源

```python
# 支持多种数据格式
- CSV (pandas.read_csv)
- Excel (pandas.read_excel)
- JSON (pandas.read_json)
- SQL (sqlalchemy + pandas)
```

### 自定义可视化

```python
# Agent 可以生成各种图表
- 折线图: 趋势分析
- 柱状图: 对比分析
- 饼图: 占比分析
- 散点图: 相关性分析
- 热力图: 相关性矩阵
```

## 📚 相关资源

- [LangChain Deep Agents 文档](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangChain 文档](https://python.langchain.com/)
- [Daytona 文档](https://www.daytona.io/docs/)
- [Pandas 文档](https://pandas.pydata.org/docs/)
- [Matplotlib 文档](https://matplotlib.org/)

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

Apache License 2.0
