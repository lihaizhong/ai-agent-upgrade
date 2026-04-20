# Plan: Resume And Continuation Contract Alignment

## Status

- Status: Implemented
- Updated: 2026-04-20
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/06-resume-and-continuation-contract-alignment/task-breakdown.md)
- Notes:
  - The scoped resume and continuation contract alignment work has been implemented in the current codebase.
  - `home --resume`, `build --resume`, `lab --resume`, and continuation-aware review entry points are now aligned with docs and tests.

## Source of Truth

This plan is derived from:

- [06-resume-and-continuation-contract-alignment spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/06-resume-and-continuation-contract-alignment/spec.md)
- [cli-and-modules.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/cli-and-modules.md)
- [state-model.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/state-model.md)
- Existing `home / build / lab / review` implementations in `agent-skills/rag-learning/scripts/`

## Objective

把平台“继续上次进度”的产品语义收敛成一套可执行 contract：

- 首页恢复不再只是状态回显
- 模块内可以直接恢复到当前上下文
- 评审入口能表达 continuation-aware 的产品动作
- 文档和 CLI surface 不再分叉

## Implementation Strategy

按“先补回归测试，再定义 continuation contract，再补模块恢复 surface，最后收口文档”的顺序推进。

依赖顺序：

1. 先锁定 `home --resume` 与模块内恢复的期望输出
2. 再补 `build / lab / review` 的 continuation surface
3. 最后对齐文档和测试

## Phase 1: Regression And Contract Definition

Scope:

- 为 `home --resume` 当前缺口补回归
- 定义 continuation contract 最小字段
- 明确无上下文时的 fallback

Expected outcome:

- 恢复语义先被测试表达，而不是边改边猜

## Phase 2: Home Resume Alignment

Scope:

- 修正 `home.py` 的 resume 输出
- 让恢复动作和目标上下文显式化
- 对齐当前状态与历史上下文的优先级

Expected outcome:

- 首页恢复成为真实可执行入口

## Phase 3: Module Continuation Surfaces

Scope:

- 新增 `build --resume`
- 新增 `lab --resume`
- 调整 `review --entry-points` 表达 continuation-aware 入口

Expected outcome:

- 用户可以在模块内继续，而不是只能回首页手动拼接

## Phase 4: Docs And Verification

Scope:

- 更新 CLI / state / module docs
- 补 continuation 回归测试
- 跑平台测试与 lint

Expected outcome:

- 文档和实现共享同一套 continuation 语义

## Checkpoints

### Checkpoint: After Phases 1-2

- [x] `home --resume` 不再只是原始状态回显
- [x] 无上下文时存在明确 fallback
- [x] continuation contract 字段稳定

### Checkpoint: Complete

- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_state_flow` 通过
- [x] `ruff check` 通过
- [x] CLI / state / module docs 审查通过

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| continuation 语义与 recommendation 语义混在一起 | Medium | 明确“resume 是恢复当前上下文”，“recommend 是建议下一步” |
| `review` continuation 过早扩成独立工作流 | Medium | 先限制为入口层 continuation-aware surface |
| 模块内恢复规则各写一套导致再次分叉 | Medium | 复用统一的 continuation 判断逻辑 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
