# Build Your Claude Code

从 0 到 1 构建 nano Claude Code-like agent，基于 [Learn Claude Code](https://learn.shareai.run/zh/) 学习路径。

## 项目简介

这个项目通过渐进式的 Loop 实现，展示 AI 编码助手的核心原理：

```
while stop_reason == "tool_use":
    response = LLM(messages, tools)
    execute tools
    append results
```

整个 Agent 的秘密就是这一个模式：不断将工具执行的结果反馈给模型，直到模型决定停止。

## 学习路径

Learn Claude Code 将 Agent 分解为 5 个正交关注点（[架构层详解](https://learn.shareai.run/zh/layers/)）：

### L1 工具与执行

Agent 能做什么。基础层：工具赋予模型与外部世界交互的能力。

| 课程 | 主题 | 行数 | 说明 |
|------|------|------|------|
| **S01** | [Agent 循环](https://learn.shareai.run/zh/s01/) | 84 | 最小 Agent 内核：while loop + 一个工具 |
| **S02** | [工具](https://learn.shareai.run/zh/s02/) | 120 | 循环不变，新工具注册到调度映射 |

### L2 规划与协调

如何组织工作。从简单的待办列表到跨 Agent 共享的依赖感知任务板。

| 课程 | 主题 | 行数 | 说明 |
|------|------|------|------|
| **S03** | [TodoWrite](https://learn.shareai.run/zh/s03/) | 176 | 无计划则漂移，先列步骤再执行 |
| **S04** | [子 Agent](https://learn.shareai.run/zh/s04/) | 151 | 子代理使用独立 messages[] |
| **S05** | [技能](https://learn.shareai.run/zh/s05/) | 187 | 按需注入知识，而非预置于 system prompt |
| **S07** | [任务系统](https://learn.shareai.run/zh/s07/) | 207 | 基于文件的任务图，编排多 Agent 工作 |

### L3 内存管理

在上下文限制内保持记忆。压缩策略让 Agent 可以无限工作而不失去连贯性。

| 课程 | 主题 | 行数 | 说明 |
|------|------|------|------|
| **S06** | [上下文压缩](https://learn.shareai.run/zh/s06/) | 205 | 三层压缩策略，支持无限会话 |

### L4 并发

非阻塞执行。后台线程和通知总线实现并行工作。

| 课程 | 主题 | 行数 | 说明 |
|------|------|------|------|
| **S08** | [后台任务](https://learn.shareai.run/zh/s08/) | 198 | 后台任务，Agent 提前思考 |

### L5 协作

多 Agent 协作。团队、消息传递和能独立思考的自主队友。

| 课程 | 主题 | 行数 | 说明 |
|------|------|------|------|
| **S09** | [Agent 团队](https://learn.shareai.run/zh/s09/) | 348 | 一个 Agent 无法完成时，通过异步邮箱委托 |
| **S10** | [团队协议](https://learn.shareai.run/zh/s10/) | 419 | 请求-响应模式驱动所有团队协商 |
| **S11** | [自主 Agent](https://learn.shareai.run/zh/s11/) | 499 | Agent 自主扫描任务板并认领，无需分配 |
| **S12** | [Worktree + 任务隔离](https://learn.shareai.run/zh/s12/) | 694 | 每个工作树独立目录，任务管理目标 |

## 目录结构

```
build-your-claude-code/
├── README.md            # 项目说明文档
├── main.py              # 主入口，提供 Loop 选择菜单
├── code/
│   ├── s01-loop.py      # S01: The Agent Loop - 最小 Agent 内核
│   ├── s02-loop.py      # S02: Tools - 工具注册与调度
│   ├── s03-loop.py      # S03: TodoWrite - 任务规划能力
│   ├── s04-loop.py      # S04: Subagents - 子代理支持
│   ├── s05-loop.py      # S05: Skills - 动态技能注入
│   ├── s06-loop.py      # S06: Compact - 上下文压缩
│   ├── s07-loop.py      # S07: Tasks - 任务图编排
│   ├── s08-loop.py      # S08: Background Tasks - 后台任务
│   ├── s09-loop.py      # S09: Agent Teams - 多 Agent 协作
│   ├── s10-loop.py      # S10: Team Protocols - 团队协议
│   ├── s11-loop.py      # S11: Autonomous Agents - 自主 Agent
│   └── s12-loop.py      # S12: Worktree + Task Isolation - 工作树隔离
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
source .venv/bin/activate && cd practice/build-your-claude-code && python main.py && cd -
```

程序会显示一个菜单让你选择要运行的 Loop 实现：

```
==================================================
  Coding Agent - Loop Selection
==================================================

  1. S01 Loop - The Agent Loop
  2. S02 Loop - Tools
  3. S03 Loop - TodoWrite

  0. Exit

Select a loop [0-3]:
```

### 直接运行特定 Loop

```bash
.venv/bin/python code/s01-loop.py
.venv/bin/python code/s02-loop.py
.venv/bin/python code/s03-loop.py
```

## Loop 实现说明

### S01 Loop - The Agent Loop

**文件**：`code/s01-loop.py`

**对应课程**：[S01: The Agent Loop](https://learn.shareai.run/zh/s01/)

**特点**：
- 展示最核心的 Agent 循环模式
- 只有 `bash` 工具，可以执行 shell 命令
- 简单直接的实现，易于理解

**核心代码**：
```python
while True:
    response = client.messages.create(messages=messages, tools=tools)
    if response.stop_reason != "tool_use":
        break
    for tool_call in response.content:
        result = execute_tool(tool_call.name, tool_call.input)
        messages.append(result)
```

**示例任务**：
1. 创建一个文件 `test_workspace/hello.py`，打印 "Hello, World!"
2. 列出当前目录的所有 Python 文件
3. 查看当前的 git 分支
4. 创建 `test_output` 目录并写入 3 个文件

### S02 Loop - Tools

**文件**：`code/s02-loop.py`

**对应课程**：[S02: Tools](https://learn.shareai.run/zh/s02/)

**特点**：
- 循环模式完全不变，只是添加了新工具
- 提供完整的文件操作能力

**工具列表**：
- `bash` - 执行 shell 命令
- `read_file` - 读取文件内容
- `write_file` - 写入文件
- `edit_file` - 编辑文件（精确替换文本）

**关键洞察**：循环模式完全没有改变，只是将新工具注册到调度映射中。

**工具调度实现**：
```python
TOOL_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
}
```

**示例任务**：
1. 读取 `main.py` 文件
2. 在 `test_workspace` 创建 `greet.py`，包含 `greet(name)` 函数
3. 编辑 `greet.py`，为函数添加 docstring
4. 读取 `greet.py` 验证编辑结果

### S03 Loop - TodoWrite

**文件**：`code/s03-loop.py`

**对应课程**：[S03: TodoWrite](https://learn.shareai.run/zh/s03/)

**特点**：
- Agent 没有计划就会漂移，先列步骤再执行
- 添加 `todo` 工具来维护任务列表
- 支持标记任务完成（pending/in_progress/completed）
- nag reminder：3 轮未更新任务时自动提醒

**新工具**：
- `todo` - 更新任务列表（items: id, text, status）

**核心实现**：
```python
class TodoManager:
    def update(self, items: list) -> str: ...
    
# 注入提醒机制
if rounds_since_todo >= 3:
    results.insert(1, {"type": "text", "text": "<reminder>Update your todos.</reminder>"})
```

**关键洞察**：规划与执行分离，Agent 先思考要做什么，再逐步执行。

**示例任务**：
1. 重构 test_workspace/hello.py：添加类型提示、docstrings、main guard
2. 创建 Python 包（__init__.py, utils.py, tests/test_utils.py）

### S04 Loop - Subagents

**文件**：`code/s04-loop.py`

**对应课程**：[S04: Subagents](https://learn.shareai.run/zh/s04/)

**特点**：
- 子代理使用独立的 messages[]，上下文隔离
- 通过 `task` 工具委托子任务
- 只返回摘要给主 Agent，主对话保持干净

**新工具**：
- `task` - 启动子代理（prompt, description）

**核心实现**：
```python
def run_subagent(prompt):
    sub_messages = [{"role": "user", "content": prompt}]  # fresh context
    for _ in range(30):
        response = client.messages.create(model=MODEL, messages=sub_messages, ...)
        # ... execute tools
    return text_parts  # Only summary returns to parent
```

**关键洞察**：进程隔离天然带来上下文隔离。

**示例任务**：
1. 委托子代理探索 test_workspace 使用的测试框架
2. 并行读取多个文件并汇总结果

### S05 Loop - Skills

**文件**：`code/s05-loop.py`

**对应课程**：[S05: Skills](https://learn.shareai.run/zh/s05/)

**特点**：
- 两层技能注入：Layer 1 元数据 + Layer 2 按需加载
- SkillLoader 扫描 skills/ 目录下的 SKILL.md
- 解析 YAML frontmatter 获取元数据

**新工具**：
- `load_skill` - 按名称加载技能内容

**核心实现**：
```python
class SkillLoader:
    def get_descriptions(self) -> str:  # Layer 1: for system prompt
    def get_content(self, name: str) -> str:  # Layer 2: full body in tool_result
```

**关键洞察**：不要把所有知识都塞进 system prompt，按需加载。

**示例任务**：
1. 查看有哪些可用技能
2. 加载 agent-builder 或 mcp-builder 技能并使用

### S06+ Loop - Compact（待实现）

**对应课程**：[S06: Compact](https://learn.shareai.run/zh/s06/)

**计划特性**：
- 三层压缩策略
- 支持无限会话
- 智能摘要和历史压缩

### S07+ Loop - Tasks（待实现）

**对应课程**：[S07: Tasks](https://learn.shareai.run/zh/s07/)

**计划特性**：
- 基于文件的任务图
- 编排多 Agent 工作流

### S08+ Loop - Background Tasks（待实现）

**对应课程**：[S08: Background Tasks](https://learn.shareai.run/zh/s08/)

**计划特性**：
- 后台任务执行
- Agent 提前思考

## 核心原理

### Agent 循环

所有 AI 编程 Agent 共享同一个循环：调用模型、执行工具、回传结果。生产级系统会在其上叠加策略、权限和生命周期层。

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

### 消息增长

观察 Agent 循环执行时 messages 数组的增长。每个工具调用结果都会追加到 messages 中，最终需要压缩策略来防止上下文溢出。

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

基于 Learn Claude Code 学习路径进一步探索：

1. **S04 Subagents**：添加子代理支持并行任务
2. **S05 Skills**：动态技能注入系统
3. **S06 Compact**：上下文压缩和摘要
4. **S07 Tasks**：基于文件的任务图编排
5. **S08 Background Tasks**：后台任务执行
6. **S09-S12 Agent Teams**：多 Agent 协作系统

## 资源

- [Learn Claude Code 完整学习路径](https://learn.shareai.run/zh/timeline/)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [Claude API 最佳实践](https://docs.anthropic.com/docs/build-with-claude/prompt-engineering/overview)
- [提示工程指南](https://www.promptingguide.ai/zh)

## 许可证

Apache 2.0
