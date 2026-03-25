# OpenCode Go 指南

> OpenCode Go 多模型 Agent 配置与使用手册。

---

## 一、OpenCode Go 套餐

### 简介

OpenCode Go 是 OpenCode 官方推出的低价订阅服务，**首月 $5，之后每月 $10**，让你能够稳定地访问精选的开源编程模型。

> 注意：OpenCode Go 目前处于 Beta 测试阶段。

### 支持的模型

| 模型 | 模型 ID | 特点 |
|------|---------|------|
| **GLM-5** | `opencode-go/glm-5` | 推理最强，AIME 92.7% |
| **Kimi K2.5** | `opencode-go/kimi-k2.5` | Agent 原生支持，256K 上下文 |
| **MiniMax M2.7** | `opencode-go/minimax-m2.7` | M2.5 增强版，更聪明 |
| **MiniMax M2.5** | `opencode-go/minimax-m2.5` | 速度最快，成本最低 |

### Token 价格（每 1M）

| 模型 | 输入 | 输出 | 缓存读取 |
|------|------|------|----------|
| GLM-5 | $1.00 | $3.20 | $0.20 |
| Kimi K2.5 | $0.60 | $3.00 | $0.10 |
| MiniMax M2.7 | - | - | - |
| MiniMax M2.5 | $0.30 | $1.20 | $0.03 |

### 使用限制

限制以美元价值计算：

| 限制 | 额度 |
|------|------|
| 每 5 小时 | $12 |
| 每周 | $30 |
| 每月 | $60 |

### 预估请求数

以下是基于典型使用模式的估算（每次请求：300-870 输入 token，55,000 缓存 token，125-200 输出 token）：

| 模型 | 每 5 小时 | 每周 | 每月 |
|------|-----------|------|------|
| GLM-5 | 1,150 | 2,880 | 5,750 |
| Kimi K2.5 | 1,850 | 4,630 | 9,250 |
| MiniMax M2.7 | 14,000 | 35,000 | 70,000 |
| MiniMax M2.5 | 20,000 | 50,000 | 100,000 |

> 提示：MiniMax M2.5 成本最低，同样的额度可以用最多请求。

### 接入方式

1. 登录 [OpenCode Zen](https://opencode.ai/auth)，订阅 Go，复制 API 密钥
2. 在 OpenCode TUI 中运行 `/connect`，选择 `OpenCode Go`
3. 运行 `/models` 查看可用模型

---

## 二、oh-my-opencode 带来的能力

### 是什么

oh-my-opencode 是一个**多模型 Agent 编排框架**，将单个 AI Agent 变成一个协调开发团队。它通过专业化的 Agent 协作完成开发任务。

**核心特点：**
- 不绑定特定模型（Claude、OpenAI、任意模型均可）
- Agent 自动编排，按任务类型分配工作
- 支持并行执行多个 Agent

### Agent 系统

oh-my-opencode 内置 11 个专业化 Agent：

| Agent | 职责 | 推荐模型 |
|-------|------|----------|
| **Sisyphus** | 主控编排，协调所有子 Agent | Claude Opus 4.6 / Kimi K2.5 |
| **Hephaestus** | 深度编码执行，处理复杂跨文件调试 | GPT-5.3 Codex |
| **Prometheus** | 战略规划，访谈式制定详细计划 | Claude Opus 4.6 |
| **Atlas** | Todo 编排执行，执行 Prometheus 计划 | Claude Sonnet 4.6 |
| **Oracle** | 架构咨询，只读顾问 | GPT-5.4 / Claude Opus |
| **Metis** | 计划差距分析，识别盲点 | Claude Opus 4.6 |
| **Momus** | 计划审查验证 | GPT-5.4 |
| **Explore** | 快速代码检索 | MiniMax M2.5 |
| **Librarian** | 文档/代码搜索 | MiniMax M2.5 |
| **Multimodal Looker** | 视觉/截图分析 | Kimi K2.5 |
| **Sisyphus-Junior** | 专注执行器，执行分配的任务 | 按 Category 决定 |

### 工作模式

| 模式 | Agent | 命令 | 说明 | 使用场景 |
|------|-------|------|------|----------|
| **Ultrawork** | Sisyphus | `ultrawork` 或 `ulw` | 全自动模式，Agent 自动规划、执行、验证 | 懒人模式，不想操心时直接用 |
| **Prometheus** | Prometheus | `@plan "任务描述"` | 访谈式规划，制定详细工作计划 | 需要精确控制任务范围和步骤时 |
| **Atlas** | Atlas | `/start-work` | 执行 Prometheus 制定的计划 | Prometheus 规划完成后执行 |
| **Hephaestus** | Hephaestus | 切换 Agent | 深度执行 Agent，处理复杂任务 | 需要深入分析和技术实现时 |
| **Sisyphus** | Sisyphus | - | 主控编排，协调所有子 Agent | 日常对话和简单任务 |

### Category 路由系统

当 Sisyphus 委托子任务时，它选择 **Category**（类别）而非具体模型。Category 自动映射到合适的模型：

| Category | 用途 | 推荐模型 |
|----------|------|----------|
| **ultrabrain** | 复杂推理、架构设计 | GLM-5 |
| **deep** | 深度编码、多文件重构 | MiniMax M2.7 |
| **quick** | 快速修改、简单任务 | MiniMax M2.5 |
| **visual-engineering** | 前端/UI/视觉任务 | Kimi K2.5 |
| **artistry** | 创意、探索性任务 | Kimi K2.5 |
| **writing** | 文本、文档、注释 | GLM-5 |
| **unspecified-high** | 通用高难度任务 | MiniMax M2.7 |
| **unspecified-low** | 通用低难度任务 | MiniMax M2.5 |

### 核心能力

#### 并行执行
Claude Code 一次处理一件事。oh-my-opencode 可以并行启动多个 Agent——同时研究、写代码、验证。像一个真正的开发团队。

#### 哈希锚定编辑
Claude Code 的 edit 工具在模型无法精确重现行时失败。oh-my-opencode 使用 `LINE#ID` 内容哈希验证，每次编辑前验证内容，解决 stale-line 问题。

#### Intent Gate（意图识别）
在执行前，Sisyphus 先分类你的真实意图——研究、实现、调查、修复——然后路由到合适的处理方式。

#### LSP + AST 工具
工作区级重命名、跳转定义、查找引用、预构建诊断、AST 感知代码重写。原生 Claude Code 没有的 IDE 精度。

#### Skills 系统
每个 Skill 带来自己的 MCP 服务器，作用域限定在任务内。上下文窗口保持干净。

---

## 三、配置指南

### 安装

```bash
# 交互式安装
bunx oh-my-opencode install

# 非交互式安装（OpenCode Go 用户）
bunx oh-my-opencode install --no-tui --claude=no --openai=no --gemini=no --copilot=no --opencode-go=yes
```

### OpenCode Go 用户的推荐配置

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-openagent.schema.json",
  "disabled_hooks": ["no-hephaestus-non-gpt"],
  
  "agents": {
    // 主控编排 - Kimi K2.5 调度能力强
    "sisyphus": { "model": "opencode-go/kimi-k2.5" },
    "sisyphus-junior": { "model": "opencode-go/kimi-k2.5" },
    
    // 推理型任务 - GLM-5 推理最强
    "metis": { "model": "opencode-go/glm-5" },
    "momus": { "model": "opencode-go/glm-5" },
    "prometheus": { "model": "opencode-go/glm-5" },
    "oracle": { "model": "opencode-go/glm-5" },
    
    // 深度编码 - MiniMax M2.7 更聪明
    "hephaestus": { "model": "opencode-go/minimax-m2.7" },
    
    // 快速执行 - MiniMax M2.5 速度快成本低
    "explore": { "model": "opencode-go/minimax-m2.5" },
    "librarian": { "model": "opencode-go/minimax-m2.5" },
    
    // 多模态 - Kimi K2.5 上下文最长
    "atlas": { "model": "opencode-go/kimi-k2.5" },
    "multimodal-looker": { "model": "opencode-go/kimi-k2.5" }
  },
  
  "categories": {
    "ultrabrain": { "model": "opencode-go/glm-5" },
    "deep": { "model": "opencode-go/minimax-m2.7" },
    "quick": { "model": "opencode-go/minimax-m2.5" },
    "visual-engineering": { "model": "opencode-go/kimi-k2.5" },
    "artistry": { "model": "opencode-go/kimi-k2.5" },
    "writing": { "model": "opencode-go/glm-5" },
    "unspecified-high": { "model": "opencode-go/minimax-m2.7" },
    "unspecified-low": { "model": "opencode-go/minimax-m2.5" }
  }
}
```

### 模型选择策略

| 任务类型 | 推荐模型 | 原因 |
|----------|----------|------|
| 复杂推理、架构决策 | GLM-5 | AIME 92.7%，推理最强 |
| 任务调度、多 Agent 协调 | Kimi K2.5 | 256K 最长上下文，Agent 原生支持 |
| 复杂编码任务 | MiniMax M2.7 | M2.5 增强版，更聪明 |
| 快速检索、简单修改 | MiniMax M2.5 | 速度快、成本低 |

### 常用命令

| 命令 | 作用 | 使用场景 |
|------|------|----------|
| `ultrawork` / `ulw` | 触发全自动工作模式 | 复杂任务，想让 Agent 全自动处理 |
| `@plan "任务描述"` | 启动 Prometheus 规划模式 | 需要详细规划和访谈的任务 |
| `/start-work` | 开始执行计划 | Prometheus 规划完成后的执行 |
| `/ralph-loop "任务"` | 自循环开发直到完成 | 长时间任务，自动继续直到 `<promise>DONE</promise>` |
| `/ulw-loop "任务"` | ultrawork 循环模式 | 全自动 + 最大强度并行执行 |
| `/refactor <目标>` | 智能重构 | 代码重构，支持 LSP、AST、架构分析 |
| `/handoff` | 生成交接文档 | 切换会话时保留上下文 |
| `/cancel-ralph` | 取消 Ralph 循环 | 中断正在运行的循环 |
| `/stop-continuation` | 停止所有继续机制 | 停止多步骤工作流 |
| `/init-deep` | 初始化 AGENTS.md | 生成项目知识库 |
| `@oracle "问题"` | 直接咨询架构问题 | 架构决策或复杂调试 |
| `@librarian "搜索内容"` | 搜索文档和代码示例 | 查找库的使用方法或最佳实践 |
| `@explore "关键词"` | 快速搜索代码库 | 查找现有代码位置 |
| `@agent-name` | 直接调用指定 Agent | 需要特定 Agent 时使用 |

### 交互式技巧

| 操作 | 作用 |
|------|------|
| 按 `Tab` | 切换到 Prometheus 规划模式 |
| 按 `Esc` (双击) | 中断当前执行 |
| `@agent-name` | 直接调用指定 Agent |

---

## 四、完整工作流程

```
用户请求
    ↓
[Intent Gate] — 分类用户意图
    ↓
[Sisyphus] — Kimi K2.5 编排调度
    ↓
    ├─→ [Prometheus] — GLM-5 战略规划
    ├─→ [Metis] — GLM-5 差距分析
    ├─→ [Momus] — GLM-5 计划审查
    ├─→ [Atlas] — Kimi K2.5 执行编排
    ├─→ [Oracle] — GLM-5 架构咨询
    ├─→ [Explore] — MiniMax M2.5 快速检索
    ├─→ [Librarian] — MiniMax M2.5 文档搜索
    └─→ [Category 路由]
              ├─→ ultrabrain → GLM-5
              ├─→ deep → MiniMax M2.7
              ├─→ quick → MiniMax M2.5
              └─→ visual-engineering → Kimi K2.5
```

---

## 五、核心原则

| 模型 | 核心定位 |
|------|----------|
| **GLM-5** | 推理型任务（Prometheus、Metis、Momus、Oracle、ultrabrain）|
| **Kimi K2.5** | 调度型任务（Sisyphus、Atlas、visual-engineering）|
| **MiniMax M2.7** | 复杂执行型任务（deep、unspecified-high）|
| **MiniMax M2.5** | 快速执行型任务（Explore、Librarian、quick）|

---

## 六、配置参考

### 配置文件位置

| 优先级 | 路径 |
|--------|------|
| 项目级 | `.opencode/oh-my-openagent.jsonc` |
| 用户级 (macOS/Linux) | `~/.config/opencode/oh-my-openagent.jsonc` |

### Agent 覆盖选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型标识符 |
| `variant` | string | 模型变体（max, high, medium, low）|
| `category` | string | 从 category 继承配置 |
| `temperature` | number | 采样温度（0-2）|
| `top_p` | number | 核采样参数（0-1）|
| `prompt` | string | 完全覆盖系统提示词 |
| `tools` | object | 启用/禁用特定工具 |
| `disable` | boolean | 禁用该 Agent |
| `maxTokens` | number | 最大响应 token 数 |

### Category 配置字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | 类别用途描述 |
| `model` | string | AI 模型 ID |
| `variant` | string | 模型变体（如 max, xhigh）|
| `temperature` | number | 创造力水平（0.0 ~ 2.0）|
| `top_p` | number | 核采样参数（0.0 ~ 1.0）|
| `tools` | object | 工具使用控制 |
| `maxTokens` | number | 最大响应 token 数 |
| `is_unstable_agent` | boolean | 标记为不稳定，强制后台模式 |

### 模型解析优先级

```
Agent 请求 → 用户配置覆盖 → Fallback 链 → 系统默认
```

### 安全 vs 危险覆盖

**安全覆盖**（同一模型家族）：
| Agent | 安全替换 |
|-------|----------|
| Sisyphus | Opus → Sonnet, Kimi K2.5, GLM 5 |
| Prometheus | Opus → GPT-5.4（自动切换 prompt）|
| Atlas | Kimi K2.5 → Sonnet, GPT-5.4 |

**危险覆盖**（无对应 prompt）：
| Agent | 警告 |
|-------|------|
| Sisyphus → GPT | 无 GPT prompt，性能严重下降 |
| Hephaestus → Claude | 为 Codex 设计，Claude 无法替代 |
| Explore → Opus | 浪费成本，检索只需速度不需要智能 |
| Librarian → Opus | 同上，文档搜索不需要深度推理 |

### 相关资源

- [官方配置参考](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/reference/configuration.md)
- [官方功能文档](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/reference/features.md)
- [官方概述](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/overview.md)

---

> 最后更新：2026-03-25
