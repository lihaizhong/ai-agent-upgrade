# AI 编程模型方案规划

> 基于 GLM-5、Kimi K2.5、MiniMax-M2.7、MiniMax-M2.5 四模型的 Agent 与 Category 映射方案。

## 模型能力概览

| 模型 | 核心优势 | 推荐用途 |
|------|----------|----------|
| **GLM-5** | 推理最强（AIME 92.7%）、长程一致性佳 | 复杂推理任务 |
| **Kimi K2.5** | Agent Swarm 原生支持、256K 最长上下文 | 任务调度、多模态 |
| **MiniMax-M2.7** | MiniMax-M2.5 增强版，更聪明 | 复杂编码任务 |
| **MiniMax-M2.5** | 工具调用 BFCL 第一、速度快、成本低 | 常规编码、快速任务 |

## OpenCode Go 额度（$10/月 ≈ ¥70）

| 模型 | 每月额度 | 特点 |
|------|----------|------|
| GLM-5 | 5,750 次 | 推理最强 |
| Kimi K2.5 | 9,250 次 | 调度最强 |
| MiniMax-M2.7 | 70,000 次 | 复杂任务 |
| MiniMax-M2.5 | 100,000 次 | 快速任务 |

---

## Agent 映射方案

oh-my-opencode 的 Agent 是实际执行工作的角色，映射如下：

| Agent | 职责 | 推荐模型 | 原因 |
|-------|------|----------|------|
| **Sisyphus** | 主控编排 | Kimi K2.5 | Agent Swarm 原生支持，并行调度能力最强 |
| **Sisyphus-Junior** | 专注执行器 | Kimi K2.5 | Atlas 下任务执行，精简版 Sisyphus |
| **Metis** | 计划差距分析 | GLM-5 | Claude-like 推理，深度分析计划漏洞和盲点 |
| **Momus** | 计划审查验证 | GLM-5 | GPT-Native，计划严格验证，只有通过才执行 |
| **Hephaestus** | 深度编码执行 | MiniMax-M2.7 | 深度编码能力，适合复杂跨文件调试和架构推理 |
| **Prometheus** | 战略规划（访谈）| GLM-5 | 深度推理，处理复杂访谈和计划制定 |
| **Atlas** | Todo 编排执行 | Kimi K2.5 | Agent Swarm 并行任务分发 |
| **Oracle** | 架构咨询 | GLM-5 | 架构决策需要强推理能力 |
| **Explore** | 快速代码检索 | MiniMax-M2.5 | 检索任务成本低、速度快即可 |
| **Librarian** | 文档/代码搜索 | MiniMax-M2.5 | 搜索任务，MiniMax-M2.5 工具调用 BFCL 第一 |
| **Multimodal Looker** | 视觉/截图分析 | Kimi K2.5 | 256K 最长上下文，多模态能力强 |

### Agent 配置

> Hephaestus 使用非 GPT 模型时需要禁用 hook，否则会被强制切换到 Sisyphus。

```jsonc
{
  "disabled_hooks": ["no-hephaestus-non-gpt"],
  "agents": {
    "sisyphus": { 
      "model": "opencode-go/kimi-k2.5",
      "ultrawork": { "model": "opencode-go/kimi-k2.5" }
    },
    "sisyphus-junior": { "model": "opencode-go/kimi-k2.5" },
    "metis": { "model": "opencode-go/glm-5" },
    "momus": { "model": "opencode-go/glm-5" },
    "hephaestus": { "model": "opencode-go/minimax-m2.7" },
    "prometheus": { "model": "opencode-go/glm-5" },
    "atlas": { "model": "opencode-go/kimi-k2.5" },
    "oracle": { "model": "opencode-go/glm-5" },
    "explore": { "model": "opencode-go/minimax-m2.5" },
    "librarian": { "model": "opencode-go/minimax-m2.5" },
    "multimodal-looker": { "model": "opencode-go/kimi-k2.5" }
  }
}
```

---

## Category 映射方案

Category 是 Sisyphus 调度子任务时的路由标签：

| Category | 用途 | 推荐模型 | 原因 |
|----------|------|----------|------|
| **ultrabrain** | 复杂推理、架构设计 | GLM-5 | AIME 92.7% 推理最强 |
| **deep** | 深度编码、多文件重构 | MiniMax-M2.7 | 更聪明，适合复杂任务 |
| **quick** | 快速修改、简单任务 | MiniMax-M2.5 | 速度快、成本低 |
| **visual-engineering** | 前端/UI/视觉任务 | Kimi K2.5 | 多模态能力强 |
| **artistry** | 创意、探索性任务 | Kimi K2.5 | 灵活思维 |
| **writing** | 文本、文档、注释 | GLM-5 | 文本生成能力强 |
| **unspecified-high** | 通用高难度任务 | MiniMax-M2.7 | 综合能力强 |

### Category 配置

```jsonc
{
  "categories": {
    "ultrabrain": { "model": "opencode-go/glm-5" },
    "deep": { "model": "opencode-go/minimax-m2.7" },
    "quick": { "model": "opencode-go/minimax-m2.5" },
    "visual-engineering": { "model": "opencode-go/kimi-k2.5" },
    "artistry": { "model": "opencode-go/kimi-k2.5" },
    "writing": { "model": "opencode-go/glm-5" },
    "unspecified-high": { "model": "opencode-go/minimax-m2.7" }
  }
}
```

---

## 完整工作流程

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
    ├─→ [Explore] — MiniMax-M2.5 快速检索
    ├─→ [Librarian] — MiniMax-M2.5 文档搜索
    └─→ [Category 路由]
              ├─→ ultrabrain → GLM-5
              ├─→ deep → MiniMax-M2.7
              ├─→ quick → MiniMax-M2.5
              └─→ visual-engineering → Kimi K2.5
```

---

## 核心原则

| 模型 | 核心定位 |
|------|----------|
| **GLM-5** | 推理型任务（Prometheus、Metis、Momus、Oracle、ultrabrain）|
| **Kimi K2.5** | 调度型任务（Sisyphus、Atlas、visual-engineering）|
| **MiniMax-M2.7** | 复杂执行型任务（deep、unspecified-high）|
| **MiniMax-M2.5** | 快速执行型任务（Explore、Librarian、quick）|

---

## 完整配置示例

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
  "disabled_hooks": ["no-hephaestus-non-gpt"],
  
  "agents": {
    "sisyphus": { 
      "model": "opencode-go/kimi-k2.5",
      "ultrawork": { "model": "opencode-go/kimi-k2.5" }
    },
    "sisyphus-junior": { "model": "opencode-go/kimi-k2.5" },
    "metis": { "model": "opencode-go/glm-5" },
    "momus": { "model": "opencode-go/glm-5" },
    "hephaestus": { "model": "opencode-go/minimax-m2.7" },
    "prometheus": { "model": "opencode-go/glm-5" },
    "atlas": { "model": "opencode-go/kimi-k2.5" },
    "oracle": { "model": "opencode-go/glm-5" },
    "explore": { "model": "opencode-go/minimax-m2.5" },
    "librarian": { "model": "opencode-go/minimax-m2.5" },
    "multimodal-looker": { "model": "opencode-go/kimi-k2.5" }
  },
  "categories": {
    "ultrabrain": { "model": "opencode-go/glm-5" },
    "deep": { "model": "opencode-go/minimax-m2.7" },
    "quick": { "model": "opencode-go/minimax-m2.5" },
    "visual-engineering": { "model": "opencode-go/kimi-k2.5" },
    "artistry": { "model": "opencode-go/kimi-k2.5" },
    "writing": { "model": "opencode-go/glm-5" },
    "unspecified-high": { "model": "opencode-go/minimax-m2.7" }
  }
}
```

---

## 使用方式

### 安装

```bash
# 交互式安装
bunx oh-my-opencode install

# 非交互式安装（OpenCode Go 用户）
bunx oh-my-opencode install --no-tui --claude=no --openai=no --gemini=no --copilot=no --opencode-go=yes
```

### 工作模式

| 模式 | 命令 | 说明 | 使用场景 |
|------|------|------|----------|
| **Ultrawork** | `ultrawork` 或 `ulw` | 全自动模式，Agent 自动规划、执行、验证 | 懒人模式，不想操心时直接用 |
| **Prometheus** | 按 `Tab` 或 `@plan "任务"` | 访谈式规划，制定详细工作计划 | 需要精确控制任务范围和步骤时 |
| **Atlas** | `/start-work` | 执行 Prometheus 制定的计划 | Prometheus 规划完成后执行 |
| **Sisyphus** | 默认主 Agent | 主控编排，协调所有子 Agent | 日常对话和简单任务 |

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
| `/git-master commit` | 智能 Git 提交 | 自动检测提交风格，拆分原子提交 |
| `/git-master rebase` | 智能变基 | 冲突解决、分支清理 |
| `/playwright` | 浏览器自动化 | 网页测试、截图、爬取 |
| `/frontend-ui-ux` | 设计开发 | 美观 UI/UX 实现 |
| `@oracle "问题"` | 直接咨询架构问题 | 架构决策或复杂调试 |
| `@librarian "搜索内容"` | 搜索文档和代码示例 | 查找库的使用方法或最佳实践 |
| `@explore "关键词"` | 快速搜索代码库 | 查找现有代码位置 |
| `@agent-name` | 直接调用指定 Agent | 需要特定 Agent 时使用 |

### 交互式技巧

| 操作 | 作用 |
|------|------|
| 按 `Tab` | 切换到 Prometheus 规划模式 |
| 按 `Ctrl+C` | 中断当前执行 |
| `@agent-name` | 直接调用指定 Agent |

### 后台任务

| 命令 | 作用 | 使用场景 |
|------|------|----------|
| `task(..., run_in_background=true)` | 后台运行任务 | 并行执行多个任务时 |
| `background_output(task_id)` | 获取后台任务结果 | 后台任务完成后查看输出 |
| `background_cancel(task_id)` | 取消后台任务 | 任务不再需要时 |

**示例**：
```
task(subagent_type="explore", prompt="查找认证实现", run_in_background=true)
# 继续其他工作...
# 完成后用 background_output 获取结果
```

### 内置 Skills

| Skill | 触发场景 | 作用 |
|-------|----------|------|
| **git-master** | commit, rebase, squash | Git 专家，自动检测提交风格，拆分原子提交 |
| **playwright** | 浏览器任务、测试 | Playwright 浏览器自动化 |
| **agent-browser** | 浏览器任务 | Agent Browser CLI 自动化 |
| **dev-browser** | 有状态浏览器脚本 | 持久化页面状态的浏览器自动化 |
| **frontend-ui-ux** | UI/UX 任务、设计 | 设计驱动的美观 UI 实现 |

### Category + Skill 组合策略

| 组合 | Category | Skills | 效果 |
|------|----------|--------|------|
| **设计师** | `visual-engineering` | `frontend-ui-ux`, `playwright` | 实现美观 UI 并浏览器验证 |
| **架构师** | `ultrabrain` | 无 | 深度架构分析和推理 |
| **维护者** | `quick` | `git-master` | 快速修复 + 干净提交 |

### 工具说明

| 工具 | 作用 | 使用场景 |
|------|------|----------|
| **grep** | 正则搜索内容 | 查找代码中的特定模式 |
| **glob** | 文件模式匹配 | 按名称查找文件 |
| **edit** | 哈希锚定编辑 | 安全精确的代码修改，不会出现 stale-line 错误 |
| **look_at** | 媒体分析 | 分析 PDF、图片、图表 |
| **session_list** | 列出所有会话 | 管理多个会话 |
| **session_search** | 会话全文搜索 | 跨会话查找信息 |
| **interactive_bash** | tmux 终端 | 运行交互式 TUI 应用（vim、htop）|

---

## Task 系统

启用 `experimental.task_system: true` 后支持：

| 命令 | 作用 |
|------|------|
| `task_create` | 创建任务（支持依赖关系）|
| `task_get` | 获取任务详情 |
| `task_list` | 列出所有任务 |
| `task_update` | 更新任务状态 |

**与 TodoWrite 的区别**：

| 特性 | TodoWrite | Task 系统 |
|------|-----------|-----------|
| 存储 | 会话内存 | 文件系统 |
| 持久性 | 关闭后丢失 | 跨会话保留 |
| 依赖 | 无 | 支持 `blockedBy` |
| 并行 | 手动管理 | 自动优化 |

---

## 配置参考

### 配置文件位置

| 优先级 | 路径 |
|--------|------|
| 项目级 | `.opencode/oh-my-opencode.jsonc` |
| 用户级 (macOS/Linux) | `~/.config/opencode/oh-my-opencode.jsonc` |

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

> 最后更新：2026-03-22
