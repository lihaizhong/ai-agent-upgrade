# Tasks: Profile Preference Rollup And Progress Semantics

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/08-profile-preference-rollup-and-progress-semantics/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/08-profile-preference-rollup-and-progress-semantics/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Preference Schema And Regression Coverage

- [x] Task: 定义 `preferences.json` 的目标 schema
  - Acceptance: 偏好键、证据来源和更新时间字段边界清楚
  - Verify: 文档审查 + 代码审查
  - Files: `docs/rag-learning-architecture/workspace-and-persistence.md`, `agent-skills/rag-learning/scripts/profile.py`

- [x] Task: 补 profile 进度和偏好回归测试
  - Acceptance: 测试能表达 stable preferences 输出和 active/completed count 语义
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_platform.py`, `tests/rag_learning/test_state_flow.py`

## Phase 2: Preference Rollup Implementation

- [x] Task: 从实验 history 聚合稳定偏好
  - Acceptance: `lab` 的 `recommended_choice` 能转成可解释的偏好证据
  - Verify: 状态流测试 + 偏好文件检查
  - Files: `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/profile.py`

- [x] Task: 从评审 history 聚合推荐栈偏好
  - Acceptance: `review` 的 `recommended_stack` 能转成 stable preferences 的组成部分
  - Verify: 状态流测试 + 偏好文件检查
  - Files: `agent-skills/rag-learning/scripts/review.py`, `agent-skills/rag-learning/scripts/profile.py`

- [x] Task: 明确 `preferences.json` 的单一真相写入路径
  - Acceptance: 偏好只由一套聚合逻辑生成，不存在双写分叉
  - Verify: 代码审查
  - Files: `agent-skills/rag-learning/scripts/profile.py`, `agent-skills/rag-learning/scripts/workspace.py`

## Phase 3: Profile Summary Alignment

- [x] Task: 扩展 `profile --summary` 的 stable preference 视图
  - Acceptance: summary 中存在 `stable_preferences` 和相应证据摘要
  - Verify: 平台测试 + CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/profile.py`

- [x] Task: 修正 project 进度统计语义
  - Acceptance: active/completed project 计数与真实状态一致
  - Verify: 平台测试 + 状态流测试
  - Files: `agent-skills/rag-learning/scripts/profile.py`, `agent-skills/rag-learning/scripts/state.py`

## Phase 4: Docs And Verification

- [x] Task: 更新 profile / workspace / overview 文档
  - Acceptance: 文档反映偏好沉淀与真实进度统计语义
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/profile.md`, `docs/rag-learning-architecture/workspace-and-persistence.md`, `docs/rag-learning-architecture/overview.md`

- [x] Task: 完成偏好聚合相关测试与 lint 验证
  - Acceptance: 平台、状态流、内容测试和 Ruff 全部通过
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow tests.rag_learning.test_content_quality` 与 `ruff check`
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [x] Gate: profile 不再只是最近 history 回看
  - Acceptance: 用户能看到真实长期偏好沉淀
  - Verify: CLI 输出检查 + 文档审查

- [x] Gate: `preferences.json` 与 `profile --summary` 没有双真相
  - Acceptance: 偏好结构和消费语义一致
  - Verify: 代码审查 + 测试
