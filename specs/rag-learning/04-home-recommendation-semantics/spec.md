# Spec Change: Home Recommendation Semantics

## Objective

收敛 `rag-learning` 首页推荐与状态层之间的职责边界，使 `recommended_next_action` 既能承载显式动作，也允许承载中性状态，但首页最终只返回可执行推荐。

本次 change 主要解决：

1. `home --recommend` 当前直接透传 state 中的 `recommended_next_action`
2. 状态层的中性值、占位值和显式动作没有边界
3. `profile --summary` 也直接回显 recommendation，容易进一步放大语义漂移
4. 后续 build / lab / review 扩展后，首页推荐会越来越容易出现 no-op 或过期动作

## Assumptions

1. `current-state.json` 仍然保留 `recommended_next_action`
2. 该字段同时服务于状态恢复和首页推荐，但这两层语义必须区分
3. 当前平台仍以 `home --recommend` 作为统一推荐入口
4. 本次 change 不重写整个推荐系统，只澄清边界并修正明显缺口

## Background

当前 `RagLearningStateStore.get_summary()` 直接返回：

- `recommendation.action = current_state.recommended_next_action`
- `recommendation.reason = current_state.last_action`

而 `HomeService.recommend()` 又直接把该值透传给用户。

这样做的风险是：

- `open_dashboard` 之类的中性值会变成最终推荐
- 历史遗留动作会被误当成当前可执行建议
- 首页层失去“消费状态后再做兜底推荐”的职责

`prompt-learning` 后续已经专门为这一问题补过 spec，`rag-learning` 应在问题扩散前先收敛。

## Scope

### 1. 区分显式动作与中性状态

`recommended_next_action` 可以包含两类值：

- 显式动作：如 `continue_learning`、`start_build`、`open_lab`
- 中性哨兵值：如 `open_dashboard`，表示“交还首页兜底逻辑”

中性值允许存在于持久化层，但不应直接成为首页最终推荐动作。

### 2. 让 `home --recommend` 先消费显式状态，再回到兜底逻辑

推荐优先级应为：

1. 显式动作
2. 当前进行中的课程 / 项目 / 实验 / 评审上下文
3. 兜底推荐

`home` 不应仅做字段转发，而应承担 recommendation mapping 和 fallback 责任。

### 3. 收敛 `profile` 中 recommendation 的语义

`profile --summary` 可以保留对当前状态 recommendation 的展示，但必须明确：

- 展示的是状态层记录
- 不等同于首页最终推荐

如有必要，可拆分为：

- `state_recommendation`
- `home_recommendation`

或保留现有字段名，但在文档中明确职责。

### 4. 对齐状态写入方

以下模块需要复核：

- `learning`
- `build`
- `lab`
- `review`

要求：

- 只写入已定义枚举
- 中性值与显式值边界清楚
- 不伪造下一步动作

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```

## Project Structure

- `agent-skills/rag-learning/scripts/home.py`
  - 首页推荐逻辑与 fallback 语义
- `agent-skills/rag-learning/scripts/state.py`
  - 推荐动作持久化与 summary 输出
- `agent-skills/rag-learning/scripts/profile.py`
  - recommendation 展示语义
- `agent-skills/rag-learning/scripts/learning.py`
- `agent-skills/rag-learning/scripts/build.py`
- `agent-skills/rag-learning/scripts/lab.py`
- `agent-skills/rag-learning/scripts/review.py`
  - 推荐动作写入方
- `docs/rag-learning-architecture/state-model.md`
- `docs/rag-learning-architecture/profile.md`

## Code Style

优先用直接分支表达“显式动作”和“中性状态”的区别，不引入复杂推荐引擎抽象。

```python
def _recommendation_from_state(action: str | None) -> dict | None:
    if action in {None, "open_dashboard"}:
        return None
    return recommendation_map.get(action)
```

约束：

- 首页最终推荐必须是可执行动作
- 中性状态只能存在于状态层，不直接暴露给用户作为下一步
- 测试必须覆盖“状态正确”和“首页推荐正确”两个层次

## Testing Strategy

- 新增或调整回归测试，覆盖：
  - fresh workspace 的 `home --recommend` 不返回 no-op
  - 中性状态不会直接透传给用户
  - 有进行中的 build / lab / review 时，首页能回到正确兜底逻辑
  - 状态写入方只使用已定义动作枚举

## Boundaries

- Always:
  - 保留状态层 recommendation 字段
  - 让首页最终推荐返回可执行动作
  - 让 state / home / profile 的语义一致
- Ask first:
  - 改动首页兜底推荐的整体产品策略
  - 新增大量 recommendation 枚举
  - 重做 profile 信息架构
- Never:
  - 把 `open_dashboard` 这类中性值继续作为首页最终推荐动作
  - 在没有真实上下文时伪造具体下一步
  - 让 `profile` 和 `home` 对同一 recommendation 给出互斥解释

## Success Criteria

- [x] `home --recommend` 不再直接透传 `recommended_next_action`
- [x] 中性状态与显式动作边界被明确写入 spec 和文档
- [x] 首页推荐始终返回可执行动作
- [x] `profile` 对 recommendation 的展示语义清楚
- [x] 状态写入方使用统一动作枚举
- [x] 相关状态流测试覆盖上述行为

## Non-Goals

- 不重写整个首页推荐策略
- 不改变平台模块边界
- 不扩展新的学习档案能力
- 不引入复杂评分或排序模型

## Open Questions

1. `profile --summary` 是否需要同时展示“状态层 recommendation”和“首页实际 recommendation”？
2. `build`/`lab`/`review` 完成后，默认回流动作应优先回首页、回 profile，还是回原上下文？
