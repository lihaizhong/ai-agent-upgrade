# AI Agent 架构分层

> 基于 Anthropic、Google、OpenAI 及学术研究（arXiv Jan 2026）的权威框架

## 一、核心层（Core）

Anthropic 称之为 **"LLM + 3个增强"**，是 Agent 能运行的最小闭环：

| 组件 | 作用 | 典型实现 |
|------|------|---------|
| **LLM 推理引擎** | 理解任务、制定计划、决定下一步 | Claude GPT-4 |
| **Tools** | 与外部世界交互（API、代码、搜索） | function calling |
| **Memory** | 维持对话状态和短期记忆 | messages 数组 |
| **Planning** | 任务分解、链式推理 | CoT, ToT |

### Agent 执行循环

```
OBSERVE → THINK → ACT → VERIFY → (循环)
```

---

## 二、重要层（Production-Required）

决定 Agent 在生产环境中是否可靠：

| 组件 | 作用 | 重要性原因 |
|------|------|-----------|
| **Critic/Verifier** | 自我验证、结果检查 | Anthropic 强调这是可靠 Agent 的关键 |
| **Guardrails** | 安全边界、权限控制 | 防止有害输出、错误操作 |
| **Routing** | 判断何时用工具、何时直接回答 | 避免过度工具调用 |
| **Observability** | 日志、追踪、调试 | 生产环境必备 |

---

## 三、增强层（Enhancement）

差异化竞争力，非必需但能提升能力上限：

| 组件 | 作用 | 适用场景 |
|------|------|---------|
| **RAG** | 知识检索增强 | 需要最新/大量事实知识的任务 |
| **Multi-Agent** | 多 Agent 协作分工 | 复杂任务分解 |
| **World Models** | 环境状态内部模拟 | 需要预测未来状态的场景 |
| **Learning/Adaptation** | 从交互中学习用户偏好 | 个性化服务 |
| **多模态感知** | 处理图像、音频 | 视觉/语音交互场景 |

---

## 四、反直觉的洞察

> **简单架构往往比复杂架构更有效**
>
> — Anthropic Research (Dec 2024)

很多情况下，单个 LLM + 工具调用的简单 Agent 比多 Agent 协作系统表现更好。

**建议优先级**：先确保核心层和重要层做到位，再考虑增强层。

---

## 五、形式化定义

arXiv 定义的 Agent 五元组：

```
A = (πθ, M, T, V, E)

πθ = Transformer policy (LLM 核心)
M  = Memory 子系统
T  = Tools (API、代码、搜索)
V  = Verifiers/Critics
E  = Environment
```

---

## 六、分层总览

| 层次 | 组件 | 必要性 | 项目实践 |
|------|------|--------|---------|
| **核心层** | LLM + Tools + Memory + Planning | 必须 | `build-your-claude-code` |
| **重要层** | Critic + Guardrails + Routing + Observability | 生产必须 | 还未涉及 |
| **增强层** | RAG + Multi-Agent + Learning | 可选 | `build-rag-agent`, `openexp` |

---

## 参考来源

- [Anthropic: Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) (Dec 2024)
- [Google Cloud: Agent Architecture Components](https://docs.cloud.google.com/architecture/choose-agentic-ai-architecture-components)
- [arXiv: AI Agent Systems Survey (2601.01743)](https://arxiv.org/abs/2601.01743) (Jan 2026)
- [OpenAI: Agents Architecture Guide](https://developers.openai.com/api/docs/guides/agents)
