# Plan: Build Progression And Completion Semantics

## Status

- Status: Proposed
- Created: 2026-04-20
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/07-build-progression-and-completion-semantics/spec.md)

## Source of Truth

This plan is derived from:

- [07-build-progression-and-completion-semantics spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/07-build-progression-and-completion-semantics/spec.md)
- [build-center.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/build-center.md)
- [state-model.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/state-model.md)
- Existing `build.py` and `state.py` implementations

## Objective

把 build 从“记录已完成步骤”收敛为“能表达下一步、完成态和跨模块 handoff”的产品状态模型：

- build progress 能恢复到真实下一步
- 完成态能被首页和档案稳定消费
- step handoff 不再只停留在展示字段

## Implementation Strategy

按“先补状态回归，再修 build progress 语义，再对齐首页/档案消费”的顺序推进。

依赖顺序：

1. 先让测试表达当前 step / completed / handoff 三类缺口
2. 再调整 `state.py` 与 `build.py`
3. 最后收口 `home.py`、`profile.py` 与文档

## Phase 1: Regression Coverage

Scope:

- 补 `current_step` 下一步语义回归
- 补 final step completed 回归
- 补 handoff 动作消费回归

Expected outcome:

- build 产品语义先被测试锁定

## Phase 2: Build Progress State Fix

Scope:

- 调整 `record_build_step()` 的 step 推进逻辑
- 增加真实 project completed 语义
- 明确 `current_step / last_completed_step / status` 的边界

Expected outcome:

- build progress 成为 resume 和 summary 可直接消费的状态源

## Phase 3: Handoff Consumption Alignment

Scope:

- 让 build step 完成消费 handoff 配置
- 对齐首页推荐与档案统计对 build 完成态的解释

Expected outcome:

- build 完成后不会再给出过期动作

## Phase 4: Docs And Verification

Scope:

- 更新 build / state / profile 文档
- 跑平台、状态流和配置测试

Expected outcome:

- 完成态语义在代码、配置、文档、测试中一致

## Checkpoints

### Checkpoint: After Phases 1-2

- [ ] `current_step` 已切换为下一步语义
- [ ] final step 可进入真实 completed 状态
- [ ] build progress 结构仍保持可解释

### Checkpoint: Complete

- [ ] `tests.rag_learning.test_platform` 通过
- [ ] `tests.rag_learning.test_state_flow` 通过
- [ ] `tests.rag_learning.test_config_units` 通过
- [ ] `ruff check` 通过
- [ ] build / state / profile 文档审查通过

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `current_step` 语义变化会影响现有测试或 handoff | Medium | 先补回归，再统一切换消费方 |
| final step 动作语义选择不当，导致首页推荐又分叉 | Medium | 在 spec 中先明确只允许保留一套最终动作口径 |
| build 进度结构过度膨胀 | Low | 只增加恢复和完成态必需字段 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_config_units
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
