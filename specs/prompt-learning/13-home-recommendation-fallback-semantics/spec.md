# Spec Change: Home Recommendation Fallback Semantics

## Objective

把 `prompt-learning` 首页推荐中的一个剩余语义缺口收敛成单一真相：

1. `open_dashboard` 是持久化层的中性状态，不是首页最终返回给用户的可执行推荐动作
2. fresh workspace 在没有更强显式动作时，应进入首页兜底推荐逻辑，而不是收到一个 no-op 的“回到首页”
3. 考试完成且无薄弱项时，`current-state.json` 仍可写入 `open_dashboard`，但首页最终推荐必须回到兜底逻辑继续给出下一步

本次 change 不扩展推荐策略，只澄清 `open_dashboard` 在状态层和首页层之间的职责边界。

## Assumptions

本规格按以下假设推进：

1. `recommended_next_action` 既承担“显式动作”角色，也允许承载少量中性哨兵值
2. `open_dashboard` 的产品语义是“当前流程完成，交还首页兜底推荐”，而不是“用户下一步再次进入首页”
3. fresh workspace 目前可接受沿用现有首页兜底规则返回默认推荐；本次不单独重设计新用户推荐策略
4. 本次 change 只修正 `home.py` 消费状态的语义，不改动考试、学习、练习模块的状态写入枚举集合

## Background

`11-review-driven-scoring-state-and-validation-fixes` 已经把“无薄弱项考试完成后”的显式状态定义为 `open_dashboard`，并明确要求“由首页兜底推荐逻辑决定下一步”。

但后续实现把 `open_dashboard` 直接映射成了首页最终推荐动作，导致两类问题：

- fresh workspace 在 bootstrap 后执行 `home --recommend`，得到 `open_dashboard`
- 无薄弱项考试完成后，虽然状态层写的是中性动作，但首页仍把它原样返回，形成 no-op 推荐

这让 state 层、home 层和测试之间再次出现了语义漂移：

- state 认为 `open_dashboard` 是中性动作
- home 把 `open_dashboard` 当成可执行推荐
- 测试一度开始断言这种 no-op 行为

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```

## Project Structure

- `agent-skills/prompt-learning/scripts/home.py`
  - 首页推荐逻辑、显式状态动作映射、兜底推荐规则
- `agent-skills/prompt-learning/scripts/state.py`
  - `recommended_next_action` 默认值和持久化结构
- `agent-skills/prompt-learning/scripts/exam.py`
  - 考试完成后写入 `open_dashboard` 的状态路径
- `tests/prompt_learning/test_platform.py`
  - fresh workspace 的首页推荐回归
- `tests/prompt_learning/test_state_flow.py`
  - 无薄弱项考试完成后的首页推荐回归
- `docs/prompt-learning-architecture/state-model.md`
  - 状态层与首页层的职责边界

## Code Style

保持现有 Python 风格，用直接分支表达“中性状态交还兜底逻辑”的语义，不引入新的抽象层。

```python
def _recommendation_from_state(self, action: str | None, interaction: dict) -> dict | None:
    if action in {None, "open_dashboard"}:
        return None
    return recommendation_map.get(action)
```

约束：

- 中性状态可以存在于持久化层，但不应被首页直接作为最终推荐返回
- 首页应先消费真正的显式动作，再在中性状态下回到兜底逻辑
- 测试必须同时覆盖“状态值正确”和“首页最终推荐正确”这两个层次

## Testing Strategy

- 采用 bug-first 回归方式，先表达 no-op 推荐缺陷，再修正实现
- 新增或调整的测试重点覆盖：
  - fresh workspace 的 `home --recommend` 不返回 `open_dashboard`
  - 无薄弱项考试完成后，`current-state.json` 仍写 `open_dashboard`
  - 无薄弱项考试完成后，`home --recommend` 回到兜底逻辑并返回可执行动作
- 保持现有 `unittest + CLI` 风格，不引入新测试框架

## Boundaries

- Always:
  - 保持 `open_dashboard` 作为持久化层允许存在的中性状态
  - 让首页最终推荐始终返回可执行动作，而不是 no-op
  - 对齐 spec、实现、测试和状态模型文档的语义
- Ask first:
  - 改动首页兜底推荐本身的优先级策略
  - 新增 `recommended_next_action` 枚举值
  - 改变 fresh workspace 的默认推荐产品方向
- Never:
  - 把 `open_dashboard` 当成首页最终推荐动作继续暴露给用户
  - 在测试中把 no-op 推荐固化为期望行为
  - 为修复这个语义问题而扩大到推荐系统整体重构

## Success Criteria

- [ ] `current-state.json` 中的 `open_dashboard` 被明确为中性状态，而非首页最终推荐动作
- [ ] fresh workspace 执行 `home --recommend` 时不会返回 `open_dashboard`
- [ ] 无薄弱项考试完成后，状态层仍写入 `open_dashboard`
- [ ] 无薄弱项考试完成后，首页最终推荐会回到兜底逻辑并给出可执行动作
- [ ] `tests.prompt_learning.test_platform` 与 `tests.prompt_learning.test_state_flow` 覆盖上述两层语义
- [ ] 相关文档不再混淆“状态中性值”和“首页推荐动作”

## Non-Goals

- 不重写首页推荐整体策略
- 不改变 fresh workspace 当前兜底推荐具体落到哪一个动作
- 不修改考试弱项识别逻辑
- 不扩展 `current-state.json` schema

## Open Questions

- 如果后续产品希望 fresh workspace 的默认推荐从当前兜底结果切换为更明确的 `open_catalog` 或其他动作，应另起一个小 spec 调整推荐策略，而不是继续复用 `open_dashboard` 这个中性状态做产品表达。
