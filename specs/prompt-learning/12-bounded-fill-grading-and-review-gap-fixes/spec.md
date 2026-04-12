# Spec Change: Bounded Fill Grading And Review Gap Fixes

## Objective

修复 `prompt-learning` 当前剩余的三个 review 缺陷，并把“填空题判题逻辑”从宽松的字符串相似度收敛成更可解释的受约束判题契约：

1. 填空题不再用高相似度直接判定“完全正确”，避免短中文术语因一字之差拿满分
2. Prompt Lab 只有在槽位完整、草稿审查全部通过、用户确认后才允许保存模板
3. 错题回练只修复了部分历史错误时，首页推荐仍应继续指向 `review_mistakes`

本次 change 继续保持现有 CLI 结构和题型结构，不引入外部依赖，也不把考试判题升级成开放式 LLM 裁判。

## Assumptions

本规格按以下假设推进：

1. 目前 `prompt-learning` 的填空题仍以“术语、范围、步骤机制”这类短答案为主，不需要开放式语义评审
2. 对填空题来说，“受约束的语义正确”应来自题目元数据和模式化判题，而不是自由文本相似度
3. `acceptable_variants` 仍是现有最稳定的同义表达入口，本次不会引入新的持久化数据源
4. Prompt Lab 的“草稿审查通过”语义是所有 checklist 项都为 `pass`，而不是“有 fail 但写了 revisions 也可保存”
5. 错题回练的目标是把未解决错误清零；只解决了一部分时，不应提前引导用户离开回练路径

## Background

当前实现虽然已经修复了 whitespace-only 的中文评分问题，但仍存在三个行为缺口：

### 1. 填空题满分条件过宽

`exam.py` 现在把 `SequenceMatcher(...).ratio() > 0.8` 视为完全正确。对短中文术语，这会把明显错误答案判成满分。

实际例子：

- 标准答案：`检索增强生成`
- 用户答案：`检索增强生存`

这两个答案只差一个字，但考试语义完全不同。当前实现会返回 `(True, 10)`，属于 correctness 回归。

### 2. Prompt Lab 保存门禁仍然漏了一层

`save_template()` 现在要求：

- 槽位完整
- 草稿结构合法
- 用户确认

但它没有要求 `review` 最终全部为 `pass`。这意味着一个仍含失败审查项的模板，只要附上 `revisions`，依然能保存到 workspace，和产品文档不一致。

### 3. 错题回练推荐和 mastery 又重新分叉

`practice.py` 已经把 `mistake_delta` 回写给 `mastery.json`，但 `state.py` 里推荐动作仍然先按 `result == good` 直接写成 `continue_learning`。

这会导致：

- 当前课程仍有未解决错题
- `mastery.json` 的 `mistake_count > 0`
- `current-state.json` 却推荐 `continue_learning`

三者同时出现，形成新的状态矛盾。

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_exam_session tests.prompt_learning.test_state_flow tests.prompt_learning.test_workspace_fallback
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```

## Project Structure

- `agent-skills/prompt-learning/scripts/exam.py`
  - 填空题判题入口、题型化判题分发、报告生成
- `agent-skills/prompt-learning/scripts/prompt_lab.py`
  - Prompt Lab 槽位校验、草稿审查校验、模板保存门禁
- `agent-skills/prompt-learning/scripts/state.py`
  - 练习完成后的显式推荐动作
- `tests/prompt_learning/test_exam_session.py`
  - 填空题评分回归测试
- `tests/prompt_learning/test_state_flow.py`
  - 错题回练推荐与 Prompt Lab 保存门禁测试
- `docs/prompt-learning-architecture/`
  - 考试、Prompt Lab、状态模型的契约文档

## Code Style

保持当前 Python 风格，优先采用“可解释的小函数 + 模式化分发”，避免重新引入模糊相似度作为满分依据。

```python
def grade_fill(self, question: dict, user_answer: str) -> tuple[bool, int]:
    mode = self._resolve_fill_grading_mode(question)
    if mode == "range":
        return self._grade_fill_range(question, user_answer)
    if mode == "steps":
        return self._grade_fill_steps(question, user_answer)
    return self._grade_fill_term(question, user_answer)
```

约束：

- 完全正确只能来自 exact / normalized exact / acceptable variants / mode-specific exact checks
- 模糊相似度最多触发部分分，不得直接给满分
- 保存门禁必须把“审查通过”定义为全部 checklist 项为 `pass`
- 推荐逻辑必须优先尊重当前持久化事实，而不是只看本次结果标签

## Testing Strategy

- 采用 bug-first 回归策略，先表达当前缺陷，再修实现
- 新增测试重点覆盖：
  - 中文短术语仅一字之差不能拿满分
  - range 特判与 whitespace-only normalization 继续成立
  - Prompt Lab 存在 `fail` 审查项时不能保存模板
  - 错题只解决一部分时，`recommended_next_action` 仍为 `review_mistakes`
- 保持现有 `unittest + CLI` 风格，不引入新的测试框架

## Boundaries

- Always:
  - 让填空题满分条件回到可解释、可证明的规则
  - 用自动化测试覆盖三个修复点
  - 对齐 spec、文档、实现、测试的行为口径
- Ask first:
  - 引入第三方 NLP / embedding / LLM 依赖做判题
  - 修改考试题型、分值或报告 schema
  - 扩展 Prompt Lab 模板持久化结构
- Never:
  - 再次使用模糊字符串相似度直接判满分
  - 在存在 `fail` 审查项时保存模板
  - 在 `mistake_count > 0` 时推荐用户离开错题回练

## Success Criteria

- [ ] `检索增强生存` 这类短中文近似错误答案不再被判为完全正确
- [ ] 空格/格式差异、`acceptable_variants`、现有 range 语义仍然有效
- [ ] 填空题判题入口按模式分发到可解释的小函数，而不是单一模糊相似度分支
- [ ] Prompt Lab 在任一 checklist 项为 `fail` 时不能保存模板
- [ ] 错题回练只修复部分错误时，`recommended_next_action` 仍为 `review_mistakes`
- [ ] `tests.prompt_learning` 全绿，`ruff check` 通过

## Non-Goals

- 不引入通用语义判题模型
- 不把填空题改成开放式主观题
- 不重构 CLI 模块结构
- 不改变 Prompt Lab 五槽位结构

## Open Questions

- 当前实现会先落一个“受约束语义判题”的接口骨架，主要覆盖 `term / range / steps` 三类模式；如果后续要接入 LLM judge，只允许它输出 `partial` 或 `needs_review`，不应直接输出 `correct`。本次 change 不实现 LLM judge。
