# Plan: Review-Driven Scoring, State, And Validation Fixes

## Status

- Status: Proposed
- Created: 2026-04-12
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/11-review-driven-scoring-state-and-validation-fixes/spec.md)

## Source of Truth

This plan is derived from:

- [11-review-driven-scoring-state-and-validation-fixes spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/11-review-driven-scoring-state-and-validation-fixes/spec.md)
- [exam-center.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/exam-center.md)
- [state-model.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/state-model.md)
- [prompt-lab.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/prompt-lab.md)
- Existing regression suites in `tests/prompt_learning/`

## Objective

用一次聚焦的实现，把 review 中确认的三个 defect 修成稳定契约：

- 填空题评分兼容中文格式差异
- 考试完成后的显式推荐动作与真实弱项一致
- Prompt Lab 对“空槽位”的判断从“空字符串”收紧到“空语义值”

## Dependency Graph

```text
Regression coverage
    │
    ├── Fill grading normalization and similarity fix
    │
    ├── Exam history recommendation fix
    │
    └── Prompt Lab blank-slot validation fix
             │
             └── Docs alignment
                      │
                      └── Full regression
```

实现顺序按“先写能失败的测试，再做最小实现，再统一文档和全量回归”推进。

## Architecture Decisions

- 使用“规范化字符串 + 中文友好的字符级比较”替代当前的空白分词相似度；不引入外部依赖。
- `recommended_next_action` 继续作为首页显式动作的真相来源，但由 `record_history()` 在写入时根据真实弱项决定是 `review_weak_topics` 还是 `open_dashboard`。
- Prompt Lab 把“纯空白字符串”视为与缺失值等价的空槽位，并在 `validate_slots()` 这一最早边界阻断无效保存。

## Implementation Strategy

### Phase 1: Regression Coverage

Scope:

- 为三个已确认问题补回归测试
- 让测试先表达目标契约，而不是先改实现

Expected outcome:

- 新增测试在当前实现上能够暴露缺陷

### Phase 2: Fill Grading Semantics

Scope:

- 规范化填空题用户答案与标准答案
- 把近似匹配从空白分词改为中文可用的比较逻辑
- 保留现有 range 特判和部分得分语义

Expected outcome:

- 中文或混合语言答案不会因格式性空白差异直接变成 0 分

### Phase 3: Exam Recommendation Alignment

Scope:

- 修正考试历史写入时的显式推荐动作
- 让“有弱项”和“无弱项”两条路径分别落到不同动作
- 如有必要，更新考试和状态模型文档

Expected outcome:

- 考试完成后，状态文件与首页推荐不再自相矛盾

### Phase 4: Prompt Lab Save Gate

Scope:

- 收紧 `validate_slots()` 对空值的定义
- 确认 `save_template()` 依赖严格槽位校验结果
- 补充模板保存的负向测试

Expected outcome:

- 纯空白槽位不能通过校验，也不能被保存

### Phase 5: Docs And Full Verification

Scope:

- 对齐 `exam-center.md`、`state-model.md`、`prompt-lab.md`
- 运行 prompt-learning 相关全量测试和 lint

Expected outcome:

- spec、文档、实现、测试表达同一套行为

## Checkpoints

### Checkpoint: After Phases 1-2

- [ ] 新增评分回归测试已存在且通过
- [ ] 填空题评分没有破坏现有英文用例
- [ ] `tests/prompt_learning/test_exam_session.py` 通过

### Checkpoint: After Phases 3-4

- [ ] 状态推荐回归测试通过
- [ ] Prompt Lab 负向保存测试通过
- [ ] CLI 输出字段未发生非预期变化

### Checkpoint: Complete

- [ ] `tests/prompt_learning` 全绿
- [ ] `ruff check` 通过
- [ ] 文档与 spec 审查通过

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 新的字符级相似度规则误伤英文或数字题 | Medium | 保留现有 exact/variant/range 分支，新增针对中英文混合输入的测试 |
| 推荐动作改为 `open_dashboard` 后，现有测试或文档仍写死 `review_weak_topics` | Medium | 先补状态回归测试，再同步更新 `state-model.md` 和 `exam-center.md` |
| `validate_slots()` 收紧后，已有测试 fixture 因空白值被判失败 | Low | 用显式非空值替换 fixture，并新增专门的负向用例 |

## Parallelization Opportunities

- Safe to parallelize:
  - 文档更新可以在核心实现稳定后单独并行处理
  - 新增测试用例可以与实现分析并行准备
- Must be sequential:
  - 评分语义修复与其测试需要一起推进
  - 推荐动作修复必须在状态文档对齐前确定最终契约
- Needs coordination:
  - 若多人并行修改 `test_state_flow.py`，需要先约定断言口径，避免围绕 `recommended_next_action` 互相覆盖

## Verification Commands

```bash
.venv/bin/ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
.venv/bin/python -m pytest tests/prompt_learning/test_exam_session.py -q
.venv/bin/python -m pytest tests/prompt_learning/test_state_flow.py -q
.venv/bin/python -m pytest tests/prompt_learning -q
```
