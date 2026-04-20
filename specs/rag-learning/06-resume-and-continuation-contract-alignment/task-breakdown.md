# Tasks: Resume And Continuation Contract Alignment

## Status

- Status: Completed
- Updated: 2026-04-20
- Notes:
  - All spec-scoped tasks and verification gates are complete in the current codebase.
  - Follow-up continuation refinements should be tracked as a new spec change.

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/06-resume-and-continuation-contract-alignment/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/06-resume-and-continuation-contract-alignment/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Regression And Contract Definition

- [x] Task: 为 `home --resume` 补 continuation contract 回归测试
  - Acceptance: 测试能区分“有可恢复上下文”和“无上下文 fallback”两类输出
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_platform.py`, `tests/rag_learning/test_state_flow.py`

- [x] Task: 定义 continuation contract 的最小字段集合
  - Acceptance: `action / target_module / target_payload / fallback_reason` 等字段边界清楚
  - Verify: 代码审查 + CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/home.py`, `docs/rag-learning-architecture/state-model.md`

## Phase 2: Home Resume Alignment

- [x] Task: 修正 `home.py` 的 resume 输出语义
  - Acceptance: `home --resume` 返回可执行 continuation contract，而不是原始状态透传
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow`
  - Files: `agent-skills/rag-learning/scripts/home.py`

- [x] Task: 对齐首页恢复的优先级规则
  - Acceptance: 当前模块、进行中上下文、最近可继续上下文和 fallback 具有稳定优先级
  - Verify: 状态流测试
  - Files: `agent-skills/rag-learning/scripts/home.py`, `agent-skills/rag-learning/scripts/state.py`

## Phase 3: Module Continuation Surfaces

- [x] Task: 新增 `build --resume`
  - Acceptance: 有进行中 project 时返回当前 project 与下一步上下文；否则回到 entry points
  - Verify: CLI 输出检查 + 平台测试
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: 新增 `lab --resume`
  - Acceptance: 有当前 topic 时返回当前实验上下文；否则回到 entry points
  - Verify: CLI 输出检查 + 平台测试
  - Files: `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/__main__.py`

- [x] Task: 让 `review --entry-points` 表达 continuation-aware 入口
  - Acceptance: 入口中可区分新建评审、继续最近评审和查看历史摘要
  - Verify: CLI 输出检查 + 平台测试
  - Files: `agent-skills/rag-learning/scripts/review.py`, `agent-skills/rag-learning/scripts/__main__.py`

## Phase 4: Docs And Verification

- [x] Task: 更新 CLI / state / module 恢复文档
  - Acceptance: 文档不再声明未实现或语义模糊的 continuation surface
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/cli-and-modules.md`, `docs/rag-learning-architecture/state-model.md`, `docs/rag-learning-architecture/build-center.md`, `docs/rag-learning-architecture/rag-lab.md`, `docs/rag-learning-architecture/architecture-review.md`

- [x] Task: 完成恢复流测试与 lint 验证
  - Acceptance: 平台测试、状态流测试和 Ruff 全部通过
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow` 与 `ruff check`
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [x] Gate: resume 与 recommend 的语义边界清楚
  - Acceptance: “恢复当前上下文” 与 “建议下一步” 没有被混成同一 contract
  - Verify: 代码审查 + 文档审查

- [x] Gate: continuation surface 在首页和模块内保持一致
  - Acceptance: 不会出现首页能恢复、模块内却无法直接继续的割裂体验
  - Verify: CLI 输出检查 + 测试
