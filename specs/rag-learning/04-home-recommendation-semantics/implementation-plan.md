# Plan: Home Recommendation Semantics

## Status

- Status: Implemented
- Updated: 2026-04-20
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/04-home-recommendation-semantics/task-breakdown.md)
- Notes:
  - The scoped home recommendation semantics work has been implemented in the current codebase.
  - Home recommendation consumption, profile summary wording, regression coverage, and docs now distinguish state-layer values from final home actions.

## Source of Truth

This plan is derived from:

- [04-home-recommendation-semantics spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/04-home-recommendation-semantics/spec.md)
- [01-learning-platform-rearchitecture spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/spec.md)
- Existing home/state/profile flows in `agent-skills/rag-learning/scripts/`

## Objective

把 `recommended_next_action` 从“状态层字段”与“首页最终推荐动作”之间的语义缺口收敛成单一真相：

- 中性状态可以留在持久化层
- 首页最终推荐只返回可执行动作
- `profile` 的 recommendation 展示不再与首页语义混淆

## Implementation Strategy

按“先补回归测试，再修状态消费，再对齐文档”的顺序推进。

依赖顺序：

1. 先定义状态层与首页层的双层断言
2. 再修 `home.py` 的 recommendation consumption
3. 再对齐 `profile` 和文档

## Architecture Decisions

- `open_dashboard` 等中性值允许保留在 `current-state.json`
- `home.py` 消费 recommendation 时，把中性值视为“无显式动作”
- `profile` 可以继续展示状态层 recommendation，但必须清楚标示其语义

## Phase 1: Regression Coverage

Scope:

- 为 fresh workspace 补首页推荐回归
- 为 build/lab/review 完成后的 recommendation 语义补回归

Expected outcome:

- 当前缺口先被测试稳定表达

## Phase 2: Home Recommendation Consumption Fix

Scope:

- 修正 `home.py` 对状态 recommendation 的消费逻辑
- 增加显式动作映射与兜底推荐顺序

Expected outcome:

- 首页只对真实显式动作做直接返回
- 中性状态不再成为 no-op 推荐

## Phase 3: Profile And State Alignment

Scope:

- 调整 `profile.py` recommendation 的展示语义
- 如有必要，调整 `state.py` summary 输出结构

Expected outcome:

- state / home / profile 三层对 recommendation 的解释一致

## Phase 4: Docs And Verification

Scope:

- 更新状态模型和 profile 文档
- 运行相关回归测试与 lint

Expected outcome:

- spec、代码、测试、文档口径一致

## Checkpoints

### Checkpoint: After Phases 1-2

- [x] fresh workspace 首页推荐不返回 no-op
- [x] 中性状态不会直接透传给用户
- [x] 显式动作映射仍保持原行为

### Checkpoint: Complete

- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_state_flow` 通过
- [x] `ruff check` 通过
- [x] state/profile 文档审查通过

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 把中性状态处理成 unknown action 后误伤其他路径 | Low | 只在首页消费层特殊处理，不扩大到写入层 |
| `profile` 与 `home` 语义仍旧混淆 | Medium | 明确区分“状态记录”和“最终推荐” |
| 测试只验证首页，不验证状态层 | Medium | 用双层断言分别校验状态值与首页最终动作 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
