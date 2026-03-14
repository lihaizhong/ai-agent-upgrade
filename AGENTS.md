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
├── AGENTS.md             # 本文件
├── README.md             # 项目说明
├── docs/                 # 文档
├── exam-result/          # 考试记录
└── notebook/             # 学习笔记
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
| **prompt-learning** | 提示词工程学习 | 学习基础知识、分析改进提示词、获取练习题、评估提示词质量 |

## 使用方式

### 快速开始

使用 iFlow CLI 通过命令行或交互式会话触发 agents 和 skills：

**命令行方式**：
```bash
iflow -p "写一篇关于 AI 的博客文章" --stream           # 触发 content-marketer
iflow -p "翻译这段文字到英文" --stream                # 触发 translate
iflow -p "帮我学习提示词工程" --stream                # 触发 prompt-learning
iflow -p "分析这个提示词有什么问题" --stream           # 触发 prompt-learning
```

**交互式会话方式**：
```bash
# 打开 iFlow
iflow

# 在会话中直接输入提示词
写一篇关于 AI 的博客文章           # 触发 content-marketer
翻译这段文字到英文                # 触发 translate
帮我学习提示词工程                # 触发 prompt-learning
分析这个提示词有什么问题           # 触发 prompt-learning
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