# Build Your Claude Code

一个学习如何构建 AI 编码助手的实践项目，展示了类似 Claude 的 Agent 核心循环模式。

## 项目简介

这个项目通过渐进式的 Loop 实现，展示 AI 编码助手的核心原理：

```
while stop_reason == "tool_use":
    response = LLM(messages, tools)
    execute tools
    append results
```

整个 Agent 的秘密就是这一个模式：不断将工具执行的结果反馈给模型，直到模型决定停止。

## 目录结构

```
build-your-claude-code/
├── main.py              # 主入口，提供 Loop 选择菜单
├── code/
│   ├── s01-loop.py      # 基础 Loop：只有 bash 工具
│   ├── s02-loop.py      # 扩展 Loop：添加文件读写编辑工具
│   └── s03-loop.py      # 高级 Loop：（待实现）
├── test_workspace/      # 测试工作目录
└── test_output/         # 测试输出目录
```

## 环境配置

### 前置要求

- Python 3.11+
- Anthropic API 密钥

### 安装依赖

```bash
# 确保在项目根目录
cd /Users/lihaizhong/Documents/Project/ai-agent-upgrade

# 使用 uv 安装依赖
uv sync
```

### 配置环境变量

在项目根目录创建 `.env` 文件：

```env
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_API_KEY=your-api-key-here
MODEL_ID=claude-sonnet-4-20250514
```

## 使用方法

### 运行主程序

```bash
cd practice/build-your-claude-code
.venv/bin/python main.py
```

程序会显示一个菜单让你选择要运行的 Loop 实现：

```
==================================================
  Coding Agent - Loop Selection
==================================================

  1. S01 Loop
  2. S02 Loop

  0. Exit

Select a loop [0-2]:
```

### 直接运行特定 Loop

你也可以直接运行特定的 Loop 文件：

```bash
.venv/bin/python code/s01-loop.py
.venv/bin/python code/s02-loop.py
```

## Loop 实现说明

### S01 Loop - 基础版本

**文件**：`code/s01-loop.py`

**特点**：
- 展示最核心的 Agent 循环模式
- 只提供 `bash` 工具，可以执行 shell 命令
- 简单直接的实现，易于理解

**示例任务**：
1. 创建一个文件 `test_workspace/hello.py`，打印 "Hello, World!"
2. 列出当前目录的所有 Python 文件
3. 查看当前的 git 分支
4. 创建 `test_output` 目录并写入 3 个文件

### S02 Loop - 扩展版本

**文件**：`code/s02-loop.py`

**特点**：
- 在 S01 的基础上添加更多工具
- 提供完整的文件操作能力：
  - `bash` - 执行 shell 命令
  - `read_file` - 读取文件内容
  - `write_file` - 写入文件
  - `edit_file` - 编辑文件（精确替换文本）

**关键洞察**：循环模式完全没有改变，只是添加了工具和处理函数。

**示例任务**：
1. 读取 `main.py` 文件
2. 在 `test_workspace` 创建 `greet.py`，包含 `greet(name)` 函数
3. 编辑 `greet.py`，为函数添加 docstring
4. 读取 `greet.py` 验证编辑结果

### S03 Loop - 高级版本

**文件**：`code/s03-loop.py`

**状态**：待实现

**建议扩展**：
- 添加代码分析工具
- 实现多文件操作
- 添加错误处理和重试机制
- 支持更复杂的任务分解

## 核心原理

### Agent 循环

整个 AI 编码助手的核心就是下面的循环：

```python
def agent_loop(messages: list):
    while True:
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM,
            messages=messages,
            tools=TOOLS,
            max_tokens=8000
        )
        messages.append({"role": "assistant", "content": response.content})

        # 如果模型没有调用工具，说明完成了
        if response.stop_reason != "tool_use":
            return

        # 执行工具调用，收集结果
        results = []
        for block in response.content:
            if isinstance(block, ToolUseBlock):
                output = execute_tool(block.name, block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })

        # 将工具结果反馈给模型
        messages.append({"role": "user", "content": results})
```

### 工具调度

通过一个简单的字典映射来处理不同的工具：

```python
TOOL_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
}
```

## 安全性

项目实现了基本的安全措施：

- **路径安全**：确保所有文件操作都在工作目录内
- **命令过滤**：阻止危险的 shell 命令
- **超时保护**：命令执行有 120 秒超时限制
- **输出限制**：限制输出长度防止内存溢出

## 退出程序

在交互式界面中，输入以下任意命令退出：
- `q`
- `exit`
- 直接按回车（空输入）
- `Ctrl+C`

## 扩展建议

你可以基于这个项目进一步探索：

1. **添加更多工具**：搜索、Git 操作、测试运行等
2. **实现策略层**：添加任务规划和分解能力
3. **上下文管理**：更好地管理对话历史和文件上下文
4. **错误恢复**：添加重试和错误处理机制
5. **性能优化**：缓存、并行工具调用等

## 资源

- [Anthropic API 文档](https://docs.anthropic.com/)
- [Claude API 最佳实践](https://docs.anthropic.com/docs/build-with-claude/prompt-engineering/overview)
- [提示工程指南](https://www.promptingguide.ai/zh)

## 许可证

Apache 2.0