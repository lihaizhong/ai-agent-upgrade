# Tasks: Bounded Fill Grading And Review Gap Fixes

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/12-bounded-fill-grading-and-review-gap-fixes/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/12-bounded-fill-grading-and-review-gap-fixes/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Regression Coverage

- [ ] Task: 为填空题满分误判补回归测试
  - Acceptance: 中文短术语仅一字之差不会再被断言为完全正确；格式性空白差异仍至少非零分
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session`
  - Files: `tests/prompt_learning/test_exam_session.py`

- [ ] Task: 为 Prompt Lab 审查失败仍可保存补回归测试
  - Acceptance: 任一 checklist 项为 `fail` 时，`save_template()` 返回 `saved = false`
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Files: `tests/prompt_learning/test_state_flow.py`

- [ ] Task: 为错题部分解决后的推荐动作补回归测试
  - Acceptance: `mistake_count > 0` 时，`recommended_next_action` 仍为 `review_mistakes`
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Files: `tests/prompt_learning/test_state_flow.py`

## Phase 2: Fill Grading

- [ ] Task: 重构填空题为模式化判题入口
  - Acceptance: `grade_fill()` 按模式分发到小函数；默认模式不要求新增字段即可工作
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session`
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/test_exam_session.py`

- [ ] Task: 收紧 term 模式的满分与部分分条件
  - Acceptance: exact / normalized exact / variants 仍是满分；高相似度最多触发部分分
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session`
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/test_exam_session.py`

## Checkpoint: Fill Grading

- [ ] `tests.prompt_learning.test_exam_session` 通过
- [ ] 现有 range 兼容行为未回退

## Phase 3: Save Gate And Recommendation Alignment

- [ ] Task: 收紧 Prompt Lab 保存门禁
  - Acceptance: 只有在槽位完整、草稿审查全部通过、用户确认后才会保存模板
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Files: `agent-skills/prompt-learning/scripts/prompt_lab.py`, `tests/prompt_learning/test_state_flow.py`

- [ ] Task: 修复错题部分解决后的推荐动作
  - Acceptance: 只要 `mistake_count > 0`，练习完成后的显式推荐动作仍为 `review_mistakes`
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Files: `agent-skills/prompt-learning/scripts/state.py`, `tests/prompt_learning/test_state_flow.py`

## Checkpoint: State Alignment

- [ ] Prompt Lab 负向门禁测试通过
- [ ] 错题部分解决场景测试通过

## Phase 4: Docs And Full Verification

- [ ] Task: 对齐考试、Prompt Lab、状态模型文档
  - Acceptance: 文档明确“填空题满分来自受约束规则”“审查未通过模板不能保存”“未清零错题继续推荐回练”
  - Verify: 文档审查
  - Files: `docs/prompt-learning-architecture/exam-center.md`, `docs/prompt-learning-architecture/prompt-lab.md`, `docs/prompt-learning-architecture/state-model.md`, `docs/prompt-learning-architecture/practice-center.md`

- [ ] Task: 完成 prompt-learning 全量回归
  - Acceptance: prompt-learning 相关测试全绿，lint 通过
  - Verify:
    - `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_exam_session tests.prompt_learning.test_state_flow tests.prompt_learning.test_workspace_fallback`
    - `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning`
  - Files: `agent-skills/prompt-learning/scripts/`, `tests/prompt_learning/`
