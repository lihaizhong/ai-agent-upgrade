# Tasks: Workspace Hardening And State Alignment

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/10-workspace-hardening-and-state-alignment/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/10-workspace-hardening-and-state-alignment/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Contract Alignment

- [ ] Task: 统一 fallback 契约
  - Acceptance: `SKILL.md`、workspace 架构文档和测试都明确 identity 缺失时进入 `defaults` workspace，而不是直接失败
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_workspace_fallback`
  - Files: `agent-skills/prompt-learning/SKILL.md`, `docs/prompt-learning-architecture/workspace-and-persistence.md`, `tests/prompt_learning/test_platform.py`, `tests/prompt_learning/test_workspace_fallback.py`

## Phase 2: Path Safety

- [ ] Task: 为 workspace 用户名增加路径安全约束
  - Acceptance: workspace 根目录下不会因恶意用户名产生越界目录
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform`
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`, `tests/prompt_learning/test_platform.py`, `tests/prompt_learning/test_workspace_fallback.py`

- [ ] Task: 为报告文件名增加安全标识
  - Acceptance: 报告文件名不再使用未经净化的原始用户名
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session`
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `agent-skills/prompt-learning/scripts/__main__.py`, `tests/prompt_learning/test_exam_session.py`

## Phase 3: State Alignment

- [ ] Task: 修复首页推荐优先级
  - Acceptance: 首页会优先返回 `current-state.json` 中的显式推荐动作
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_state_flow`
  - Files: `agent-skills/prompt-learning/scripts/home.py`, `tests/prompt_learning/test_state_flow.py`, `tests/prompt_learning/test_platform.py`

- [ ] Task: 修复错题回练与 mastery 统计失真
  - Acceptance: 错题 resolved 后，mastery 能反映修正结果而不是只累计错误
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Files: `agent-skills/prompt-learning/scripts/practice.py`, `agent-skills/prompt-learning/scripts/state.py`, `tests/prompt_learning/test_state_flow.py`

## Phase 4: Prompt Lab Save Gate

- [ ] Task: 收紧模板保存前置条件
  - Acceptance: 缺槽位、未通过校验、未确认三种情况都不能保存模板
  - Verify: `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow`
  - Files: `agent-skills/prompt-learning/scripts/prompt_lab.py`, `tests/prompt_learning/test_state_flow.py`, `docs/prompt-learning-architecture/prompt-lab.md`

## Phase 5: Docs And Verification

- [ ] Task: 对齐状态与持久化文档
  - Acceptance: 文档与实现对 `recommended_next_action`、错题回练、Prompt Lab 保存边界的描述一致
  - Verify: 文档审查
  - Files: `docs/prompt-learning-architecture/state-model.md`, `docs/prompt-learning-architecture/practice-center.md`, `docs/prompt-learning-architecture/prompt-lab.md`

- [ ] Task: 完成全量回归
  - Acceptance: prompt-learning 测试全绿，lint 通过
  - Verify: 
    - `UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_state_flow tests.prompt_learning.test_exam_session tests.prompt_learning.test_workspace_fallback`
    - `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning`
  - Files: `tests/prompt_learning/`, `agent-skills/prompt-learning/scripts/`
