# Tasks: Home Recommendation Semantics

## Status

- Status: Completed
- Updated: 2026-04-20
- Notes:
  - All spec-scoped tasks and verification gates are complete in the current codebase.
  - State-layer recommendation storage remains in place, but final home recommendation behavior is now explicitly separated.

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/04-home-recommendation-semantics/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/04-home-recommendation-semantics/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Regression Coverage

- [x] Task: 补 fresh workspace 首页推荐回归测试
  - Acceptance: fresh workspace 的 `home --recommend` 不返回 no-op 动作
  - Verify: `python -m unittest tests.rag_learning.test_platform`
  - Files: `tests/rag_learning/test_platform.py`

- [x] Task: 补状态层与首页层双层推荐回归测试
  - Acceptance: 状态层可写中性值，但首页最终推荐回到兜底逻辑
  - Verify: `python -m unittest tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_state_flow.py`

## Phase 2: Implementation

- [x] Task: 修正 `home.py` 对中性 recommendation 的消费语义
  - Acceptance: `home --recommend` 只对真实显式动作做直接映射
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow`
  - Files: `agent-skills/rag-learning/scripts/home.py`

- [x] Task: 收敛显式动作映射与兜底推荐顺序
  - Acceptance: 有显式动作时优先返回；否则按当前上下文进入兜底推荐
  - Verify: CLI 输出检查 + 状态流测试
  - Files: `agent-skills/rag-learning/scripts/home.py`

## Phase 3: Profile And State Alignment

- [x] Task: 对齐 `profile.py` recommendation 展示语义
  - Acceptance: `profile --summary` 不再与 `home --recommend` 混淆同一层语义
  - Verify: 输出结构审查 + 测试
  - Files: `agent-skills/rag-learning/scripts/profile.py`

- [x] Task: 审查 `state.py` summary 的 recommendation 表达并确认无需额外调整
  - Acceptance: 状态层字段继续表达“记录值”而非“最终推荐”，且无需新增 state 层改动也能满足 contract
  - Verify: 代码审查
  - Files: `agent-skills/rag-learning/scripts/state.py`

## Phase 4: Docs And Verification

- [x] Task: 更新状态模型与档案文档
  - Acceptance: 文档清楚区分状态层 recommendation 与首页最终推荐
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/state-model.md`, `docs/rag-learning-architecture/profile.md`

- [x] Task: 完成相关测试与 lint 验证
  - Acceptance: 平台测试、状态流测试和 Ruff 全部通过
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow` 与 `ruff check`
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [x] Gate: 首页最终推荐始终是可执行动作
  - Acceptance: 不再把中性状态直接暴露给用户
  - Verify: 代码审查 + 测试

- [x] Gate: 状态层与首页层语义被明确拆分
  - Acceptance: state / home / profile 三层没有互斥解释
  - Verify: 代码审查 + 文档审查
