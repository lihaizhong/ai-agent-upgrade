# Spec Change: Review-Driven Scoring, State, And Validation Fixes

## Objective

修复 `prompt-learning` 在本轮代码审查中确认的三个缺陷，并把它们收敛成可实现、可测试、可解释的行为契约：

1. 填空题评分对中文和混合语言答案的格式差异过于脆弱
2. 考试完成后的显式推荐动作与真实弱项数据不一致
3. Prompt Lab 把纯空白字符串当作有效槽位，导致无效模板有机会落盘

本次 change 只修正已确认的问题，不扩展平台能力，也不重构模块结构。

## Assumptions

本规格按以下假设推进；如有一项不对，后续实现前应先改 spec：

1. 考试完成后，只有在本次结果确实存在 `weak_courses` 或 `weak_topics` 时，才应显式推荐 `review_weak_topics`
2. 当考试结果没有薄弱项时，显式推荐动作应回到中性状态 `open_dashboard`，由首页兜底推荐逻辑决定下一步
3. 填空题“近似正确”的判断应兼容中文，不得依赖英文空格分词
4. Prompt Lab 的五个固定槽位语义不变，只收紧“空值”的定义
5. 本次修复不引入任何第三方依赖

## Background

本轮 review 已确认以下实现问题：

### 1. 中文填空题近似匹配失真

`exam.py` 当前的 `_calculate_similarity()` 基于空白分词后做集合相似度。这对英文短语尚可工作，但对中文答案基本无效。

例如：

- 标准答案：`检索增强生成`
- 用户答案：`检索增强 生成`

这类仅有格式差异的答案，当前会被判成 `(False, 0)`，不符合“轻微格式差异不应导致直接 0 分”的评分预期。

### 2. 考试后推荐动作与真实结果断裂

`record_history()` 当前无论 `weak_courses` / `weak_topics` 是否为空，都会把：

- `last_action = exam_completed`
- `recommended_next_action = review_weak_topics`

写入 `current-state.json`。

这导致满分或无薄弱点的考试结果也会把首页推荐推向“回看薄弱点”，与真实数据不一致。

### 3. Prompt Lab 槽位校验过宽

`validate_slots()` 当前把 `""` 视为空，但把 `"   "` 这类纯空白字符串视为有效值。`save_template()` 又依赖该校验结果，因此理论上可以把“视觉上已填写、语义上为空”的模板保存到 workspace。

这违反了 Prompt Lab “先补齐槽位、再校验、再确认、最后保存”的产品边界。

## Commands

```bash
.venv/bin/ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
.venv/bin/python -m pytest tests/prompt_learning -q
.venv/bin/python -m pytest tests/prompt_learning/test_exam_session.py -q
.venv/bin/python -m pytest tests/prompt_learning/test_state_flow.py -q
```

## Project Structure

- `agent-skills/prompt-learning/scripts/exam.py`
  - 填空题评分、考试历史写入、考试完成后的推荐动作
- `agent-skills/prompt-learning/scripts/prompt_lab.py`
  - 槽位校验、草稿校验、模板保存门禁
- `agent-skills/prompt-learning/scripts/home.py`
  - 首页消费 `recommended_next_action` 的显式动作映射
- `docs/prompt-learning-architecture/exam-center.md`
  - 考试完成后的产品语义
- `docs/prompt-learning-architecture/state-model.md`
  - `recommended_next_action` 的状态规则
- `docs/prompt-learning-architecture/prompt-lab.md`
  - Prompt Lab 保存前置条件
- `tests/prompt_learning/`
  - 回归测试与 CLI 级别验证

## Code Style

保持现有 Python 风格和“直接、可解释”的实现方式。优先修正边界判断，不引入抽象堆叠。

```python
def _has_weaknesses(weak_courses: list[int], weak_topics: list[str]) -> bool:
    return bool(weak_courses or weak_topics)


def _is_blank_slot_value(value: object) -> bool:
    return isinstance(value, str) and not value.strip()
```

约束：

- 评分应先做规范化，再做比较
- 显式推荐动作必须与持久化的真实结果一致
- 保存门禁应在最早的校验边界识别空白值

## Testing Strategy

- 采用 bug-first 回归策略：先补能表达缺陷的测试，再改实现
- 重点覆盖三类新增回归：
  - 中文或混合语言填空题对格式性空白差异不直接判 0 分
  - `weak_courses=[]` 且 `weak_topics=[]` 的考试历史不会写入 `review_weak_topics`
  - Prompt Lab 的纯空白槽位不能通过 `validate_slots()`，也不能通过 `save_template()`
- 保持现有 CLI/集成测试风格，优先扩展 `tests/prompt_learning/`

## Boundaries

- Always:
  - 让评分、状态和保存边界与实际持久化数据保持一致
  - 用自动化测试覆盖三个 review 发现
  - 保持现有 CLI 输出字段稳定
- Ask first:
  - 修改考试后的默认推荐枚举集合
  - 调整 Prompt Lab 固定五槽位结构
  - 引入更复杂的语义相似度算法或外部依赖
- Never:
  - 继续依赖英文空格分词来判断中文填空题近似正确
  - 在无薄弱项时伪造 `review_weak_topics`
  - 允许未填实质内容的模板落盘到 workspace

## Success Criteria

- [ ] 填空题评分在中文或混合语言输入下，对仅有格式性空白差异的答案不再直接判 0 分
- [ ] 近似评分逻辑仍保留现有“完全正确 / 部分得分 / 错误”的三级结果语义
- [ ] 考试历史写入后，只有在真实存在弱项时才会把 `recommended_next_action` 设为 `review_weak_topics`
- [ ] 当考试结果不存在弱项时，显式推荐动作改为 `open_dashboard`
- [ ] `validate_slots()` 会把纯空白字符串识别为空槽位
- [ ] `save_template()` 无法保存包含纯空白必填槽位的模板
- [ ] `tests/prompt_learning` 全绿，`ruff check` 通过

## Non-Goals

- 不重写填空题评分体系
- 不改变考试蓝图、题型、分值或报告结构
- 不引入复杂 NLP 相似度模型
- 不扩展 Prompt Lab 槽位数量或模板 schema
- 不重构首页推荐整体策略

## Open Questions

- 当前规格采用 `open_dashboard` 作为“考试完成且无弱项”的显式中性动作；如果产品想改成更积极的 `continue_learning`，应另起一份小规格做推荐策略调整，而不是在本次 bug fix 中顺手改变。
