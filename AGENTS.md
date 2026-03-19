# AI Agent 学习项目

专注于提示词工程和上下文工程的实践项目，基于 iFlow CLI 进行探索和学习。

## 核心方向

- **提示词工程**：设计和优化提示词以获得更好的 AI 输出
- **上下文工程**：有效管理和利用上下文信息提升 Agent 性能
- **Agent 实践**：通过配置和使用预定义的 agents 和 skills 进行实践

## 项目结构

```
ai-agent-upgrade/
├── .iflow/               # iFlow 配置目录
├── .venv/                # Python 虚拟环境（使用 uv 管理）
├── AGENTS.md             # 本文件
├── README.md             # 项目说明
├── docs/                 # 文档
├── exam-result/          # 考试记录
├── notebook/             # 学习笔记
└── practice/             # 实践项目
    ├── build-custom-rag-agent/
    ├── build-data-analysis-agent/
    ├── build-rag-agent/
    ├── build-semantic-search-engine/
    ├── build-sql-agent/
    ├── build-voice-agent/
    └── build-your-claude-code/
```

## Agents

| 名称 | 用途 | 特点 |
|------|------|------|
| **content-marketer** | 撰写营销内容 | SEO 优化、内容日历、行动号召 |
| **novel-creator** | 创作爽文小说 | 快速节奏、高吸引力 |
| **perception-agent** | 内容感知分析 | 读取理解、提取关键信息、综合分析 |
| **translate** | 多语言翻译 | 保持意思、语气、风格，准确转换术语 |

## Skills

| 名称 | 用途 | 适用场景 |
|------|------|----------|
| **doc-coauthoring** | 结构化文档协作 | 提案、技术规范、决策文档 |
| **internal-comms** | 内部沟通内容 | 3P 更新、公司通讯、FAQ、状态报告 |
| **poetry** | 中国古诗词检索展示 | 按作者、标题、关键词检索唐诗宋词等 |
| **prompt-learning** | 提示词工程学习 | 学习模式（17门课程）、考试模式（四级难度）、分析改进提示词 |

## 实践项目

| 项目名称 | 说明 | 技术栈 |
|---------|------|--------|
| **build-your-claude-code** | 构建 Claude 风格的 AI 编码助手 | Python, Anthropic API |
| **build-rag-agent** | 构建 RAG（检索增强生成）Agent | Python, 向量数据库 |
| **build-custom-rag-agent** | 构建自定义 RAG Agent | Python, LangChain |
| **build-data-analysis-agent** | 构建数据分析 Agent | Python, Pandas |
| **build-semantic-search-engine** | 构建语义搜索引擎 | Python, 向量检索 |
| **build-sql-agent** | 构建 SQL 查询 Agent | Python, 数据库 |
| **build-voice-agent** | 构建语音交互 Agent | Python, 语音识别/合成 |

### 环境配置

项目使用 `uv` 管理 Python 依赖和虚拟环境：

```bash
# 安装依赖
uv sync

# 添加新依赖
uv add <package-name>

# 运行脚本
.venv/bin/python <script.py>
```

### 实践项目示例

**build-your-claude-code** 项目展示了 AI Agent 的核心循环模式：

```python
while stop_reason == "tool_use":
    response = LLM(messages, tools)
    execute tools
    append results
```

运行方式：

```bash
cd practice/build-your-claude-code
.venv/bin/python main.py
```

## 使用方式

### 环境准备

```bash
# 克隆项目
git clone <repo-url>
cd ai-agent-upgrade

# 安装依赖（使用 uv）
uv sync

# 激活虚拟环境（可选，直接使用 .venv/bin/python 即可）
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 快速开始

使用 iFlow CLI 通过命令行或交互式会话触发 agents 和 skills：

**命令行方式**：
```bash
iflow -p "写一篇关于 AI 的博客文章" --stream           # 触发 content-marketer
iflow -p "翻译这段文字到英文" --stream                # 触发 translate
iflow -p "展示李白的静夜思" --stream                  # 触发 poetry
iflow -p "帮我学习提示词工程" --stream                # 触发 prompt-learning
iflow -p "我要参加提示词考试" --stream                # 触发 prompt-learning 考试模式
```

**交互式会话方式**：
```bash
# 打开 iFlow
iflow

# 在会话中直接输入提示词
写一篇关于 AI 的博客文章           # 触发 content-marketer
翻译这段文字到英文                # 触发 translate
展示李白的静夜思                  # 触发 poetry
帮我学习提示词工程                # 触发 prompt-learning
我要参加提示词考试                # 触发 prompt-learning 考试模式
```

### 添加新配置

在 `.iflow/` 目录下：

- **Agent**：在 `agents/` 创建 `.md` 文件，遵循 YAML 前置元数据格式
- **Skill**：在 `skills/` 创建目录和 `SKILL.md` 文件，参考现有配置

## 资源

- 提示工程指南：https://www.promptingguide.ai/zh
- 学习路径：参考 `prompt-learning` skill 中的学习路径建议

## 贡献

1. 保持文档清晰准确
2. 遵循 Apache 2.0 许可证
3. 更新配置时同步更新本文档
4. 使用 `.editorconfig` 定义的代码风格
5. 添加新依赖时使用 `uv add` 而非 `pip install`
6. 运行实践项目时确保使用虚拟环境中的 Python 解释器