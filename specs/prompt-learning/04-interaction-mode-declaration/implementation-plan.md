# Plan: Prompt Learning Interaction Mode Declaration

## Status

- Status: Completed
- Created: 2026-04-08
- Completed: 2026-04-09
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/04-interaction-mode-declaration/spec.md)

## Source of Truth

This plan is derived from:

- [03-selector-first-interaction spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/03-selector-first-interaction/spec.md)
- [04-interaction-mode-declaration spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/04-interaction-mode-declaration/spec.md)
- [SKILL.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.opencode/skills/prompt-learning/SKILL.md)
- [idea one-pager](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/ideas/stable-selector-interaction-protocol.md)

## Objective

给脚本的所有用户交互输出添加 `interaction` 字段，显式声明交互模式（`selector` / `open_ended` / `inform`），消除 LLM 需要自行推断交互模式的不稳定行为。

## Implementation Strategy

采用增量修改策略：只在现有脚本输出的 dict 中添加 `interaction` 字段，不改变 `question` 对象结构，不新增 CLI 命令。

依赖顺序：

1. 先改脚本，为所有输出点加 `interaction` 字段
2. 再改 SKILL.md，加入选择器渲染协议
3. 验证脚本输出和行为一致性

## Phase 1: Script — home.py

Scope:

- `get_dashboard()`: 加 `interaction.mode = "selector"`（已有 `question`）
- `get_resume_target()`: 加 `interaction.mode = "open_ended"` + `prompt_hint`
- `get_recommendation()`: 加 `interaction.mode = "open_ended"` + `prompt_hint`

Why first: home 是用户进入平台的第一步，`get_dashboard` 已经有 `question`，是验证 selector 模式的最佳起点。

Expected outcome: `home --dashboard`、`home --resume`、`home --recommend` 输出均包含 `interaction` 字段。

## Phase 2: Script — learning.py

Scope:

- `get_catalog()`: 加 `interaction.mode = "selector"`（顶层和每个 category 的 `question` 旁）
- `get_category()`: 加 `interaction.mode = "selector"`
- `recommend_course()`: 加 `interaction.mode = "open_ended"` + `prompt_hint`
- `get_lesson_meta()`: 加 `interaction.mode = "inform"`
- `get_lesson_panel()`: 加 `interaction.mode = "selector"`（已有 `question`）
- `get_code_meta()`: 加 `interaction.mode = "inform"`
- `get_code_outline()`: 加 `interaction.mode = "inform"`
- `complete_course()`: 加 `interaction.mode = "inform"`

Why second: learning 是最高频交互模块，覆盖选择器、开放式和纯信息三种模式。

## Phase 3: Script — practice.py

Scope:

- `get_entry_points()`: 加 `interaction.mode = "selector"`（已有 `question`）
- `get_resume_target()`: 加 `interaction.mode = "open_ended"` + `prompt_hint`
- `build_blueprint()`: 加 `interaction.mode = "open_ended"` + `prompt_hint`
- `record_result()`: 加 `interaction.mode = "inform"`
- `list_open_mistakes()`: 加 `interaction.mode = "inform"`
- `get_practice_summary()`: 加 `interaction.mode = "inform"`

## Phase 4: Script — exam.py

Scope:

- `get_entry_points()`: 加 `interaction.mode = "selector"`（已有 `question`）
- `build_exam_blueprint()`: 加 `interaction.mode = "inform"`
- `generate_exam_structure()`: 加 `interaction.mode = "inform"`
- `ExamService.get_history_summary()`: 加 `interaction.mode = "inform"`

## Phase 5: Script — prompt_lab.py

Scope:

- `build_workflow()`: 加 `interaction.mode = "inform"`
- `build_interview_blueprint()`: 顶层加 `interaction.mode = "inform"` + `note`，每个 slot 加 `interaction.mode = "open_ended"` + `prompt_hint`
- `build_review_checklist()`: 加 `interaction.mode = "inform"`
- `validate_slots()`: 加 `interaction.mode = "inform"`
- `validate_draft()`: 加 `interaction.mode = "inform"`
- `PromptLabService.save_template()`: 加 `interaction.mode = "inform"`
- `PromptLabService.list_templates()`: 加 `interaction.mode = "inform"`

Why this order: prompt_lab 的 slot 级别需要特殊处理（slot 内嵌 `interaction`），放在最后确保其他模块已验证通过。

## Phase 6: Script — profile.py

Scope:

- `get_summary()`: 加 `interaction.mode = "inform"`
- `get_progress()`: 加 `interaction.mode = "inform"`
- `get_mistakes()`: 加 `interaction.mode = "inform"`
- `get_exam_history()`: 加 `interaction.mode = "inform"`
- `get_templates()`: 加 `interaction.mode = "inform"`

Why 此阶段: profile 全部是 inform 模式，变更风险最低。

## Phase 7: SKILL.md — 选择器渲染协议

Scope:

- 在"选择器优先"小节后新增"选择器渲染协议"子节
- 包含三种模式的行为规则
- 包含字段映射规则（selector 模式下 question 对象到工具参数的映射）
- 包含退化声明规则
- 包含缺少 interaction 字段时的处理规则

Why 最后: 先让脚本侧就位，再更新行为约束。

## Phase 8: Verification

Scope:

- 运行 `ruff check .opencode/skills/prompt-learning/scripts`
- 逐模块验证脚本输出包含正确的 `interaction` 字段
- 手动验证一个完整的 home → catalog → course 流程，确认 selector 正确渲染
- 手动验证一个 open_ended 场景（如 recommend_course），确认 LLM 没有强行把推荐改成选择器

## Verification Commands

```bash
ruff check .opencode/skills/prompt-learning/scripts
```

```bash
cd .opencode/skills/prompt-learning && uv run python -m scripts home --dashboard | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts home --resume | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts home --recommend | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts learning --catalog | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts practice --entry-points | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts exam --entry-points | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts lab --interview-blueprint | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts lab --workflow | python -m json.tool | grep -A5 interaction
cd .opencode/skills/prompt-learning && uv run python -m scripts profile --summary | python -m json.tool | grep -A5 interaction
```

## Risks

1. **遗漏输出点**：通过规格表格完整列出所有 29 个输出点来缓解
2. **Prompt Lab slot 内嵌 interaction 增加复杂度**：通过分别在顶层和 slot 级别独立声明来缓解
3. **SKILL.md 协议条款过长增加 LLM 认知负荷**：通过使用枚举式规则（3 种模式各一段）而非长文叙述来缓解
