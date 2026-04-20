# Tasks: Build Progression And Completion Semantics

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/07-build-progression-and-completion-semantics/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/07-build-progression-and-completion-semantics/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Regression Coverage

- [ ] Task: 补 build 当前步骤推进语义回归测试
  - Acceptance: 完成某个 step 后，测试能区分“刚完成的 step”和“下一步 current_step”
  - Verify: `python -m unittest tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_state_flow.py`

- [ ] Task: 补 final step completed 语义回归测试
  - Acceptance: 完成最终 step 后，project 会进入真实 `completed` 状态
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_platform.py`, `tests/rag_learning/test_state_flow.py`

- [ ] Task: 补 build handoff 动作消费回归测试
  - Acceptance: step handoff 不再只存在返回 payload，而会影响状态层下一步动作
  - Verify: `python -m unittest tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_state_flow.py`

## Phase 2: Build Progress State Fix

- [ ] Task: 调整 build progress 的下一步字段语义
  - Acceptance: `current_step` 指向下一步；必要时补 `last_completed_step`
  - Verify: 状态流测试 + JSON 结构检查
  - Files: `agent-skills/rag-learning/scripts/state.py`

- [ ] Task: 引入真实 project completed 语义
  - Acceptance: final step 完成后写入 `status = completed` 及稳定完成态字段
  - Verify: 平台测试 + 状态流测试
  - Files: `agent-skills/rag-learning/scripts/state.py`, `agent-skills/rag-learning/scripts/build.py`

## Phase 3: Handoff Consumption Alignment

- [ ] Task: 让 build step completion 消费 handoff 配置
  - Acceptance: step 完成后会把 `continue_build / open_lab / start_review` 等动作正确写入状态层
  - Verify: 状态流测试
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/state.py`

- [ ] Task: 对齐首页与档案对 build 完成态的消费
  - Acceptance: 首页不会继续推荐过期 build；档案不会把 completed project 算作 active
  - Verify: 平台测试 + 状态流测试
  - Files: `agent-skills/rag-learning/scripts/home.py`, `agent-skills/rag-learning/scripts/profile.py`

## Phase 4: Docs And Verification

- [ ] Task: 更新 build / state / profile 文档
  - Acceptance: 文档清楚表达下一步 step、completed 语义和 handoff 消费规则
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/build-center.md`, `docs/rag-learning-architecture/state-model.md`, `docs/rag-learning-architecture/profile.md`, `docs/rag-learning-architecture/workspace-and-persistence.md`

- [ ] Task: 完成 build 完成态相关测试与 lint 验证
  - Acceptance: 平台、状态流、配置测试和 Ruff 全部通过
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow tests.rag_learning.test_config_units` 与 `ruff check`
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [ ] Gate: build 状态能回答“刚完成了什么”和“下一步做什么”
  - Acceptance: 不再只有 completed step 列表，没有下一步语义
  - Verify: 代码审查 + 测试

- [ ] Gate: completed project 不会继续污染 active / resume / recommend 语义
  - Acceptance: completed 和 in-progress 的消费边界清楚
  - Verify: 代码审查 + 文档审查 + 测试
