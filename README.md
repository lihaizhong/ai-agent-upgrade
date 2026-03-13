# AI Agent 学习项目

AI Agent 学习之路，主要包含提示词工程、上下文工程等技术探索。

## 📚 学习资源

- [提示工程指南](https://www.promptingguide.ai/zh) - 系统学习提示词工程

## 🚀 快速开始

使用 iFlow CLI 通过命令行或交互式会话触发 `prompt-learning` skill 进行学习：

**命令行方式**：
```bash
iflow -p "帮我学习提示词工程" --stream                # 开始学习基础知识
iflow -p "分析这个提示词有什么问题" --stream           # 分析改进提示词
iflow -p "给我一些提示词练习题" --stream              # 获取练习题
iflow -p "评估这个提示词的质量" --stream              # 评估提示词质量
```

**交互式会话方式**：
```bash
# 打开 iFlow
iflow

# 在会话中直接输入提示词
帮我学习提示词工程                # 开始学习基础知识
分析这个提示词有什么问题           # 分析改进提示词
给我一些提示词练习题              # 获取练习题
评估这个提示词的质量              # 评估提示词质量
```

更多 Agents 和 Skills 的使用方式详见 [AGENTS.md](AGENTS.md)。

## 📖 笔记分类

### 基础技术（入门）

- [01 - 零样本提示](notebook/01-zero-shot-prompting.md) - 入门 | 提示技术 | 2022 | Wei et al.
- [02 - 少样本提示](notebook/02-few-shot-prompting.md) - 入门 | 提示技术 | 2020 | Brown et al.

### 推理技术（核心）

- [03 - 思维链提示](notebook/03-chain-of-thought-prompting.md) - 中级 | 推理技术 | 2022 | Wei et al.
- [04 - 自我一致性](notebook/04-self-consistency.md) - 中级 | 推理技术 | 2022 | Wang et al.
- [05 - 思维树](notebook/05-tree-of-thought.md) - 高级 | 推理技术 | 2023 | Yao et al. / Long

### 知识技术（中级）

- [06 - 生成知识提示](notebook/06-knowledge-prompting.md) - 中级 | 知识技术 | 2022 | Liu et al.
- [07 - 检索增强生成（RAG）](notebook/07-retrieval-augmented-generation.md) - 高级 | 知识技术 | 2020 | Lewis et al.

### 任务分解（高级）

- [08 - 链式提示](notebook/08-prompt-chaining.md) - 高级 | 任务分解 | 2023 | Multiple

### 工具使用（高级）

- [09 - ReAct 框架](notebook/09-react-reason-act.md) - 高级 | 工具技术 | 2022 | Yao et al.
- [10 - 程序辅助语言模型（PAL）](notebook/10-program-aided-language-models.md) - 高级 | 工具技术 | 2022 | Gao et al.
- [11 - 自动推理并使用工具（ART）](notebook/11-automatic-reasoning-and-tool-use.md) - 专家 | 工具技术 | 2022 | Paranjape et al.

### 提示优化（进阶）

- [12 - 自动提示工程师（APE）](notebook/12-automatic-prompt-engineer.md) - 专家 | 优化技术 | 2022 | Zhou et al.
- [13 - 主动提示（Active-Prompt）](notebook/13-active-prompt.md) - 专家 | 优化技术 | 2023 | Diao et al.
- [14 - 方向性刺激提示（DSP）](notebook/14-directional-stimulus-prompting.md) - 专家 | 优化技术 | 2023 | Li et al.

### 前沿技术（最新）

- [15 - 自我反思（Reflexion）](notebook/15-reflexion.md) - 专家 | 前沿技术 | 2023 | Shinn et al.
- [16 - 多模态思维链](notebook/16-multimodal-cot.md) - 专家 | 前沿技术 | 2023 | Zhang et al.
- [17 - 图形提示（GraphPrompts）](notebook/17-graph-prompts.md) - 专家 | 前沿技术 | 2023 | Liu et al.

## 🛠️ Skills & Agents

本项目包含预配置的 AI Agents 和 Skills，详见 [AGENTS.md](AGENTS.md)。

## 📝 许可证

Apache License 2.0
