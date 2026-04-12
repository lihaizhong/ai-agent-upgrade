# Plan: Home Recommendation Fallback Semantics

## Status

- Status: Proposed
- Created: 2026-04-13
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/13-home-recommendation-fallback-semantics/spec.md)

## Source of Truth

This plan is derived from:

- [13-home-recommendation-fallback-semantics spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/13-home-recommendation-fallback-semantics/spec.md)
- [11-review-driven-scoring-state-and-validation-fixes spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/11-review-driven-scoring-state-and-validation-fixes/spec.md)
- [10-workspace-hardening-and-state-alignment spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/10-workspace-hardening-and-state-alignment/spec.md)
- Existing home/state regression suites in `tests/prompt_learning/`

## Objective

用一次聚焦的收敛，把 `open_dashboard` 从“首页最终推荐动作”纠正回“交还兜底推荐逻辑的中性状态”，并为 fresh workspace 与无薄弱项考试完成场景补上稳定回归。

## Dependency Graph

```text
Regression coverage
    │
    ├── Home recommendation state-consumption fix
    │
    └── Docs alignment
             │
             └── Full verification
```

实现顺序按“先补回归测试，再修首页状态消费逻辑，再对齐文档与全量验证”推进。

## Architecture Decisions

- `open_dashboard` 保留在状态层，作为允许持久化的中性哨兵值。
- `home.py` 在消费状态时，把 `open_dashboard` 视为“没有更强显式动作”，因此继续走兜底推荐逻辑。
- 测试分两层表达契约：一层验证状态文件，一层验证首页最终推荐结果。

## Implementation Strategy

### Phase 1: Regression Coverage

Scope:

- 为 fresh workspace 首页推荐补回归测试
- 为“无薄弱项考试完成后”的首页推荐补双层断言

Expected outcome:

- 当前缺陷能先被测试稳定表达出来

### Phase 2: Home Recommendation Consumption Fix

Scope:

- 修正 `home.py` 对 `open_dashboard` 的消费语义
- 保持其他显式动作的映射不变

Expected outcome:

- 首页只对真实显式动作做直接返回
- `open_dashboard` 不再成为 no-op 推荐

### Phase 3: Docs And Verification

Scope:

- 对齐状态模型文档中的职责边界描述
- 运行相关测试和 lint

Expected outcome:

- spec、代码、测试、文档口径一致

## Checkpoints

### Checkpoint: After Phases 1-2

- [ ] fresh workspace 首页推荐回归通过
- [ ] 无薄弱项考试完成后的状态/推荐双层断言通过
- [ ] 其他显式动作映射没有回归

### Checkpoint: Complete

- [ ] `tests.prompt_learning.test_platform` 通过
- [ ] `tests.prompt_learning.test_state_flow` 通过
- [ ] `ruff check` 通过
- [ ] 文档语义审查通过

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 把 `open_dashboard` 当作未知动作忽略后，可能误伤其他依赖它的分支 | Low | 只在首页消费层特殊处理，不改动状态写入结构 |
| 测试只验证首页推荐，遗漏状态层语义 | Medium | 对无薄弱项考试场景保留双层断言：状态值与最终推荐分开验证 |
| 文档仍把 `open_dashboard` 写成用户动作 | Medium | 同步检查 `state-model.md` 相关段落，保持“中性状态”措辞一致 |

## Parallelization Opportunities

- Safe to parallelize:
  - 文档更新可在实现确定后独立完成
  - 回归测试调整可以与实现分析并行准备
- Must be sequential:
  - 首页消费语义修复必须在回归测试定义后进行
- Needs coordination:
  - 若后续还要改 fresh workspace 默认推荐策略，应基于本 spec 再起独立小 change，避免把语义修复和策略调整混在一起

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```
