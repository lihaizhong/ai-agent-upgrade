# Tasks: Home Recommendation Fallback Semantics

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/13-home-recommendation-fallback-semantics/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/13-home-recommendation-fallback-semantics/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Regression Coverage

- [ ] Task: 补 fresh workspace 首页推荐回归测试
  - Description: 在 `test_platform.py` 中补一个最小回归，用 fresh workspace 表达“首页推荐不能把 `open_dashboard` 当最终动作返回”。
  - Acceptance:
    - [ ] 测试能表达 fresh workspace 的 `home --recommend` 不返回 `open_dashboard`
    - [ ] 测试不依赖推荐系统整体重构
  - Verification:
    - [ ] `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform`
  - Dependencies: None
  - Files likely touched:
    - `tests/prompt_learning/test_platform.py`
  - Estimated scope: XS

- [ ] Task: 补无薄弱项考试完成后的双层推荐回归测试
  - Description: 在 `test_state_flow.py` 中同时断言状态层仍写 `open_dashboard`，但首页最终推荐回到兜底逻辑。
  - Acceptance:
    - [ ] `current-state.json` 的 `recommended_next_action` 仍为 `open_dashboard`
    - [ ] `home --recommend` 不返回 `open_dashboard`
  - Verification:
    - [ ] `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Dependencies: None
  - Files likely touched:
    - `tests/prompt_learning/test_state_flow.py`
  - Estimated scope: XS

## Phase 2: Implementation

- [ ] Task: 修正首页对中性状态 `open_dashboard` 的消费语义
  - Description: 让 `home.py` 仅把真正的显式动作直接映射为推荐；遇到 `open_dashboard` 时返回 `None` 并继续执行兜底推荐逻辑。
  - Acceptance:
    - [ ] `open_dashboard` 不再作为首页最终推荐动作返回
    - [ ] `review_mistakes`、`review_weak_topics`、`continue_exam` 等显式动作保持原行为
  - Verification:
    - [ ] `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_state_flow`
  - Dependencies: Task 1, Task 2
  - Files likely touched:
    - `agent-skills/prompt-learning/scripts/home.py`
  - Estimated scope: XS

## Phase 3: Docs And Verification

- [ ] Task: 对齐状态模型与回归说明
  - Description: 确认相关文档和 spec 描述 `open_dashboard` 为中性状态，不再把它表述成首页最终动作。
  - Acceptance:
    - [ ] `state-model.md` 与 spec 表达一致
    - [ ] 测试命名和断言不再固化 no-op 推荐
  - Verification:
    - [ ] 文档审查
  - Dependencies: Task 3
  - Files likely touched:
    - `docs/prompt-learning-architecture/state-model.md`
    - `tests/prompt_learning/`
  - Estimated scope: XS

- [ ] Task: 完成相关测试与 lint 验证
  - Description: 运行 prompt-learning 相关回归和 Ruff，确认本次语义修复没有引入其他状态消费回归。
  - Acceptance:
    - [ ] `tests.prompt_learning.test_platform` 通过
    - [ ] `tests.prompt_learning.test_state_flow` 通过
    - [ ] `ruff check` 通过
  - Verification:
    - [ ] `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_state_flow`
    - [ ] `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning`
  - Dependencies: Task 4
  - Files likely touched:
    - `agent-skills/prompt-learning/scripts/`
    - `tests/prompt_learning/`
  - Estimated scope: S

## Checkpoint: Complete

- [ ] `open_dashboard` 的状态层与首页层语义已拆分清楚
- [ ] fresh workspace 和无薄弱项考试两个场景都有自动化覆盖
- [ ] 变更可以继续作为后续推荐策略调整的稳定基础
