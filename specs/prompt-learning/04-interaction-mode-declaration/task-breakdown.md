# Tasks: Prompt Learning Interaction Mode Declaration

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/04-interaction-mode-declaration/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/04-interaction-mode-declaration/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Script — home.py

- [x] Task: Add `interaction` field to `get_dashboard()` output
  - Acceptance: `home --dashboard` 输出包含 `interaction.mode == "selector"`
  - Verify: `uv run python -m scripts home --dashboard | python -m json.tool` 检查 interaction 字段
  - Files: `scripts/home.py`

- [x] Task: Add `interaction` field to `get_resume_target()` output
  - Acceptance: `home --resume` 输出包含 `interaction.mode == "open_ended"` 和 `prompt_hint`
  - Verify: `uv run python -m scripts home --resume | python -m json.tool` 检查 interaction 字段
  - Files: `scripts/home.py`

- [x] Task: Add `interaction` field to `get_recommendation()` output
  - Acceptance: `home --recommend` 输出包含 `interaction.mode == "open_ended"` 和 `prompt_hint`
  - Verify: `uv run python -m scripts home --recommend | python -m json.tool` 检查 interaction 字段
  - Files: `scripts/home.py`

## Phase 2: Script — learning.py

- [x] Task: Add `interaction` field to `get_catalog()` output（顶层和每个 category）
  - Acceptance: `learning --catalog` 输出的顶层和每个 category 均包含 `interaction.mode == "selector"`
  - Verify: `uv run python -m scripts learning --catalog | python -m json.tool` 检查 interaction 字段
  - Files: `scripts/learning.py`

- [x] Task: Add `interaction` field to `get_category()` output
  - Acceptance: `learning --category 基础课程` 输出包含 `interaction.mode == "selector"`
  - Verify: `uv run python -m scripts learning --category 基础课程 | python -m json.tool`
  - Files: `scripts/learning.py`

- [x] Task: Add `interaction` field to `recommend_course()` output
  - Acceptance: 输出包含 `interaction.mode == "open_ended"` 和 `prompt_hint`
  - Verify: `uv run python -m scripts learning --recommend-course | python -m json.tool`
  - Files: `scripts/learning.py`

- [x] Task: Add `interaction.mode == "inform"` to `get_lesson_meta()`, `get_code_meta()`, `get_code_outline()`, `complete_course()` outputs
  - Acceptance: 四个输出均包含 `interaction.mode == "inform"`
  - Verify: 逐一调用命令检查 interaction 字段
  - Files: `scripts/learning.py`

## Phase 3: Script — practice.py

- [x] Task: Add `interaction` field to `get_entry_points()` output
  - Acceptance: `practice --entry-points` 输出包含 `interaction.mode == "selector"`
  - Verify: `uv run python -m scripts practice --entry-points | python -m json.tool`
  - Files: `scripts/practice.py`

- [x] Task: Add `interaction` field to `get_resume_target()` and `build_blueprint()` outputs
  - Acceptance: `practice --resume` 和 `practice --blueprint` 输出包含 `interaction.mode == "open_ended"` 及 `prompt_hint`
  - Verify: 逐一调用命令检查 interaction 字段
  - Files: `scripts/practice.py`

- [x] Task: Add `interaction.mode == "inform"` to `record_result()`, `list_open_mistakes()`, `get_practice_summary()` outputs
  - Acceptance: 三个输出均包含 `interaction.mode == "inform"`
  - Verify: 逐一调用命令检查 interaction 字段
  - Files: `scripts/practice.py`

## Phase 4: Script — exam.py

- [x] Task: Add `interaction` field to `get_entry_points()` output
  - Acceptance: `exam --entry-points` 输出包含 `interaction.mode == "selector"`
  - Verify: `uv run python -m scripts exam --entry-points | python -m json.tool`
  - Files: `scripts/exam.py`

- [x] Task: Add `interaction.mode == "inform"` to `build_exam_blueprint()`, `generate_exam_structure()`, `ExamService.get_history_summary()` outputs
  - Acceptance: 三个输出均包含 `interaction.mode == "inform"`
  - Verify: 逐一调用命令检查 interaction 字段
  - Files: `scripts/exam.py`

## Phase 5: Script — prompt_lab.py

- [x] Task: Add `interaction.mode == "inform"` to `build_workflow()`, `build_review_checklist()`, `validate_slots()`, `validate_draft()`, `save_template()`, `list_templates()` outputs
  - Acceptance: 六个输出均包含 `interaction.mode == "inform"`
  - Verify: 逐一调用命令检查 interaction 字段
  - Files: `scripts/prompt_lab.py`

- [x] Task: Add nested `interaction` to `build_interview_blueprint()` — top-level `inform` with `note`, each slot `open_ended` with `prompt_hint`
  - Acceptance: 顶层 `interaction.mode == "inform"` + `note`；每个 slot 包含 `interaction.mode == "open_ended"` + `prompt_hint`
  - Verify: `uv run python -m scripts lab --interview-blueprint | python -m json.tool` 检查嵌套 interaction 字段
  - Files: `scripts/prompt_lab.py`

## Phase 6: Script — profile.py

- [x] Task: Add `interaction.mode == "inform"` to all profile outputs
  - Acceptance: `get_summary()`, `get_progress()`, `get_mistakes()`, `get_exam_history()`, `get_templates()` 均包含 `interaction.mode == "inform"`
  - Verify: 逐一调用命令检查 interaction 字段
  - Files: `scripts/profile.py`

## Phase 7: SKILL.md — 选择器渲染协议

- [x] Task: Add "选择器渲染协议" subsection to SKILL.md after "选择器优先"
  - Acceptance: SKILL.md 的"行为准则"部分包含"选择器渲染协议"子节，涵盖三种模式规则、字段映射规则、退化声明规则、缺少 interaction 的处理规则
  - Verify: 检查 SKILL.md 内容确认协议完整
  - Files: `.opencode/skills/prompt-learning/SKILL.md`（注意：SKILL.md 的实际路径可能在嵌套目录中）

## Phase 8: Verification

- [x] Task: Run `ruff check` on scripts directory
  - Acceptance: No linting errors
  - Verify: `ruff check .opencode/skills/prompt-learning/scripts`

- [x] Task: Verify all 29 script output points contain correct `interaction` field
  - Acceptance: 每个输出点的 `interaction.mode` 与 spec 表格一致
  - Verify: 逐一运行所有 CLI 命令并检查输出

- [ ] Task: Manual verification of selector rendering in a full flow
  - Acceptance: home → catalog → category → course flow 中所有 selector 正确使用 `question` 工具渲染
  - Verify: 手动执行完整流程（当前已完成 CLI 输出与协议验证，真实执行器渲染需在交互环境中单独确认）

- [ ] Task: Manual verification of open_ended rendering
  - Acceptance: `recommend_course` 场景下 LLM 使用自然语言推荐而非退化为编号列表
  - Verify: 手动执行（当前已完成 CLI 输出与协议验证，真实执行器行为需在交互环境中单独确认）

## Global Verification Gates

- [x] Gate: All script outputs have `interaction` field before SKILL.md update
  - Acceptance: Phase 1-6 全部完成且验证通过后，再执行 Phase 7
  - Verify: 检查 task 完成状态

- [x] Gate: SKILL.md protocol matches script output behavior
  - Acceptance: 协议中的三种模式定义与脚本中的 `interaction.mode` 值完全一致
  - Verify: 交叉比对 spec 表格和 SKILL.md 协议文本

## Verification Notes

- 2026-04-09：已完成脚本级与 CLI 级验证，覆盖 home / learning / practice / exam / lab / profile 的用户可见输出点，并确认 `selector`、`open_ended`、`inform` 三种模式与 spec 一致。
- 2026-04-09：`.venv/bin/ruff check agent-skills/prompt-learning/scripts` 通过，`PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall agent-skills/prompt-learning/scripts` 通过。
- 保留未勾选的两项手动验证是因为它们依赖真实 AI 执行器的选择器渲染与对话行为，无法在当前 CLI 环境中程序化证明；这不是脚本实现缺失。
