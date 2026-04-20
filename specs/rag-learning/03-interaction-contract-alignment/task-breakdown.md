# Tasks: Interaction Contract Alignment

## Status

- Status: Completed
- Updated: 2026-04-20
- Notes:
  - All spec-scoped tasks and verification gates are complete in the current codebase.
  - Audit-confirmed no-op items are treated as completed alignment work rather than deferred follow-ups.

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/03-interaction-contract-alignment/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/03-interaction-contract-alignment/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Script Audit

- [x] Task: 审计主要脚本输出点并标注交互模式
  - Acceptance: 形成 `selector / open_ended / inform` 的输出点清单
  - Verify: 审查脚本输出表
  - Files: `agent-skills/rag-learning/scripts/`

## Phase 2: Script Alignment

- [x] Task: 统一 `home` 的 selector 结构
  - Acceptance: `home --dashboard` 输出使用顶层 `question`，`interaction.mode == "selector"`
  - Verify: CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/home.py`

- [x] Task: 为 `learning` 输出补齐 `interaction.mode`
  - Acceptance: `catalog / path / recommend-course / lesson-meta / complete` 等输出具备明确模式
  - Verify: CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/learning.py`

- [x] Task: 为 `build` 输出补齐 `interaction.mode`
  - Acceptance: `entry-points / step-panel / record-step` 输出具备明确模式
  - Verify: CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/build.py`

- [x] Task: 为 `lab` 输出补齐 `interaction.mode`
  - Acceptance: `entry-points / blueprint / history / record-result` 输出具备明确模式
  - Verify: CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/lab.py`

- [x] Task: 为 `review` 输出补齐 `interaction.mode`
  - Acceptance: `entry-points / template / history / record-summary` 输出具备明确模式
  - Verify: CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/review.py`

- [x] Task: 为 `profile` 输出补齐 `interaction.mode`
  - Acceptance: `summary / progress / experiments / reviews` 输出统一为 `inform`
  - Verify: CLI 输出检查
  - Files: `agent-skills/rag-learning/scripts/profile.py`

## Phase 3: Contract Alignment

- [x] Task: 更新 `SKILL.md` 中的 selector-first 交互规则
  - Acceptance: `SKILL.md` 明确 selector-first 和退化条件
  - Verify: 文档审查
  - Files: `agent-skills/rag-learning/SKILL.md`

- [x] Task: 对齐内容测试期望，并确认现有 eval 无需额外改动
  - Acceptance: 内容测试不再允许关键 surface 退化为纯文本菜单，且现有 eval 断言与该 contract 不冲突
  - Verify: 内容测试审查 + `evals.json` 复核
  - Files: `agent-skills/rag-learning/evals/evals.json`, `tests/rag_learning/test_content_quality.py`

## Phase 4: Verification

- [x] Task: 为 selector/open-ended/inform 增加结构断言
  - Acceptance: 平台测试能识别三类交互模式
  - Verify: `python -m unittest tests.rag_learning.test_platform`
  - Files: `tests/rag_learning/test_platform.py`

- [x] Task: 完成 lint 与内容测试验证
  - Acceptance: `ruff check` 和内容测试通过
  - Verify: `python -m unittest tests.rag_learning.test_content_quality`
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [x] Gate: 所有 selector 输出统一为顶层 `question`
  - Acceptance: 不再存在 `interaction.question` 这类私有嵌套 contract
  - Verify: 代码审查 + CLI 输出检查

- [x] Gate: 开放式与纯展示输出不会伪造选择器
  - Acceptance: `open_ended` 和 `inform` 的边界清楚
  - Verify: 代码审查 + 测试
