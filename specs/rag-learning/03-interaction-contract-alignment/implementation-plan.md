# Plan: Interaction Contract Alignment

## Status

- Status: Implemented
- Updated: 2026-04-20
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/03-interaction-contract-alignment/task-breakdown.md)
- Notes:
  - The scoped interaction contract alignment work has been implemented in the current codebase.
  - Major user-facing surfaces now declare `interaction.mode`, selector outputs use top-level `question`, and the selector-first guidance is documented.

## Source of Truth

This plan is derived from:

- [03-interaction-contract-alignment spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/03-interaction-contract-alignment/spec.md)
- [01-learning-platform-rearchitecture spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/spec.md)
- [SKILL.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/rag-learning/SKILL.md)
- Existing CLI outputs in `agent-skills/rag-learning/scripts/`

## Objective

给 `rag-learning` 的主要用户面脚本输出补齐稳定交互 contract：

- 所有输出都声明 `interaction.mode`
- selector 场景统一使用顶层 `question`
- open-ended / inform 场景边界清晰
- `SKILL.md` 与 eval/test 一起强化 selector-first 规则

## Implementation Strategy

采用增量修改策略：只补齐和统一脚本输出字段，不重写业务逻辑，不改变 CLI 命令结构。

依赖顺序：

1. 先审计并统一脚本输出
2. 再更新 `SKILL.md` 与 eval/test
3. 最后做整体验证

## Phase 1: Script Audit

Scope:

- 枚举所有主要用户面输出点
- 标出 selector / open_ended / inform 三类交互
- 确认 `home` 当前 contract 与其他模块的差异

Expected outcome:

- 形成完整交互面清单，避免遗漏输出点

## Phase 2: Script Alignment

Scope:

- 统一 `home / learning / build / lab / review / profile` 输出结构
- 将 selector 场景的 `question` 上提为顶层字段
- 为非 selector 输出补齐 `interaction.mode`

Expected outcome:

- 所有主要输出点都有稳定交互声明

## Phase 3: Contract And Guidance Alignment

Scope:

- 更新 `SKILL.md`
- 对齐 `evals/evals.json` 与内容测试期望
- 明确 selector-first 与退化规则

Expected outcome:

- 脚本 contract 与 agent guidance 一致

## Phase 4: Verification

Scope:

- 为 selector / open_ended / inform 增加结构断言
- 跑 CLI 与内容测试
- 做一轮 contract 审查

Expected outcome:

- 交互模式可以通过自动化验证稳定识别

## Checkpoints

### Checkpoint: After Phases 1-2

- [x] 主要脚本输出点都已分类
- [x] `home` 的 selector 结构与其他模块一致
- [x] `question` 不再嵌在私有结构中

### Checkpoint: Complete

- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_content_quality` 通过
- [x] `ruff check` 通过
- [x] `SKILL.md` / eval / tests 语义一致

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 漏掉某个输出点，导致 contract 半统一 | Medium | 先做脚本输出审计，再逐模块落地 |
| selector-first 改动与现有测试结构冲突 | Low | 用增量测试断言 `interaction.mode` 和顶层 `question` |
| 过度把开放式内容 selector 化 | Medium | 在 spec 中只覆盖真正的 choice-based surfaces |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_content_quality
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
