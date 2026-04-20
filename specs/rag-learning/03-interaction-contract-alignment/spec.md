# Spec Change: Interaction Contract Alignment

## Objective

为 `rag-learning` 的所有用户面脚本输出补齐一致的交互声明，使 agent 不再依赖“猜测”来决定选择器、开放式追问或纯展示行为。

本次 change 主要解决：

1. 当前各模块的 `interaction` 结构不一致
2. `home` 把 `question` 嵌进 `interaction`，其他模块又使用不同形态
3. 某些输出点没有显式交互模式，LLM 只能自行推断
4. 结构化选择存在，但还没有稳定的 selector-first contract

## Assumptions

1. `rag-learning` 仍然是平台型 skill，核心模块不变：
   - `workspace`
   - `home`
   - `learning`
   - `build`
   - `lab`
   - `review`
   - `profile`
2. 当前执行器优先支持结构化选择器
3. 本次 change 的重点是交互 contract，不是重做业务逻辑
4. `question` 仍然是 selector 场景的结构化数据源

## Background

第一轮平台化重构已经让多个模块开始返回结构化 JSON，但 contract 还不够稳定：

- 有的输出点包含 `interaction`
- 有的输出点只有 `question`
- 有的输出点完全没有交互声明
- `home.dashboard()` 的结构与其他模块不一致

这会导致：

- 相同类型的交互在不同模块表现不一致
- agent 退化成纯文本菜单的概率上升
- 后续测试无法稳定判断“这是不是一个 selector surface”

## Scope

### 1. 为所有输出点声明 `interaction.mode`

所有用户面脚本输出都应显式提供：

```json
{
  "interaction": {
    "mode": "selector" | "open_ended" | "inform"
  }
}
```

规则：

- `selector`: 当前执行器应使用原生结构化选择
- `open_ended`: 由 agent 自然语言推进
- `inform`: 纯信息展示，无需交互设计

### 2. 收敛 `question` contract

当 `interaction.mode == "selector"` 时：

- `question` 必须位于顶层，而不是嵌套在 `interaction` 内
- `question` 字段结构保持稳定
- `label` / `description` / `value` 视为结构化 contract，不允许重写成 ad hoc 文本

建议统一形态：

```json
{
  "interaction": {"mode": "selector"},
  "question": {
    "header": "RAG Home",
    "question": "你现在想推进哪一步？",
    "options": [...]
  }
}
```

### 3. 审计主要模块的交互面

至少覆盖以下输出：

- `home --dashboard`
- `home --resume`
- `home --recommend`
- `learning --catalog`
- `learning --path`
- `learning --recommend-course`
- `learning --lesson-meta`
- `build --entry-points`
- `build --step-panel`
- `build --record-step`
- `lab --entry-points`
- `lab --blueprint`
- `lab --history`
- `review --entry-points`
- `review --template`
- `review --history`
- `profile --summary`
- `profile --progress`
- `profile --experiments`
- `profile --reviews`

### 4. 对齐 `SKILL.md` 与测试

需要明确：

- selector-first 是默认规则
- 只有执行器明确不支持结构化选择时，才允许退化为文本列表
- 如果脚本定义了 selector surface，就不应在文档或 eval 中再鼓励纯文本菜单

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_content_quality
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```

## Project Structure

- `agent-skills/rag-learning/scripts/home.py`
- `agent-skills/rag-learning/scripts/learning.py`
- `agent-skills/rag-learning/scripts/build.py`
- `agent-skills/rag-learning/scripts/lab.py`
- `agent-skills/rag-learning/scripts/review.py`
- `agent-skills/rag-learning/scripts/profile.py`
- `agent-skills/rag-learning/SKILL.md`
- `agent-skills/rag-learning/evals/evals.json`
- `tests/rag_learning/`

## Code Style

只做 contract 收敛，不引入新的抽象层。优先通过小改动补齐字段和统一结构。

```python
return {
    "module": "home",
    "interaction": {"mode": "selector"},
    "question": {
        "header": "RAG Home",
        "question": "你现在想推进哪一步？",
        "options": HOME_CARDS,
    },
}
```

约束：

- `interaction.mode` 必填
- `selector` 场景必须同时提供顶层 `question`
- `inform` 场景不要伪造选择器

## Testing Strategy

- 为主要 selector surface 增加结构断言
- 为 inform/open-ended 输出增加 mode 断言
- 内容测试应覆盖 `SKILL.md` 和 eval 中的 selector-first 约束

## Boundaries

- Always:
  - 让脚本明确声明交互模式
  - 让 `question` 成为稳定结构化 contract
  - 通过测试减少文本菜单回退
- Ask first:
  - 新增交互模式枚举
  - 扩展 `question` schema
  - 将开放式教学内容强行改成选择器
- Never:
  - 在 `selector` 场景下把 `question` 嵌入任意私有结构
  - 依赖 agent 猜测某个输出是 selector 还是 inform
  - 用纯文本编号菜单替代已有结构化选择

## Success Criteria

- [x] 所有主要用户面输出都包含 `interaction.mode`
- [x] `selector` 输出统一为顶层 `question`
- [x] `home` 与其他模块的 selector 结构一致
- [x] `SKILL.md` 明确 selector-first 规则
- [x] 测试可以稳定识别 selector / open_ended / inform 三类输出

## Non-Goals

- 不重做产品信息架构
- 不修改模块边界
- 不引入新 UI 框架
- 不增加新的平台能力

## Open Questions

1. 是否需要为 `question` 增加稳定 `id` 字段以便后续测试和消费？
2. `build --step-panel` 这类输出应保持 `inform`，还是补一个轻量 follow-up selector？
