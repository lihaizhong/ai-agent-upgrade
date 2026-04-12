# Tasks: Review-Driven Scoring, State, And Validation Fixes

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/11-review-driven-scoring-state-and-validation-fixes/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/11-review-driven-scoring-state-and-validation-fixes/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Regression Coverage

- [ ] Task: 为三个 review 缺陷补最小回归测试
  - Description: 在现有 `tests/prompt_learning/` 中补三个失败前置用例，分别表达中文填空题格式差异评分、无弱项考试后的推荐动作、以及 Prompt Lab 纯空白槽位保存失败。
  - Acceptance:
    - [ ] 测试能表达“中文答案仅有空白差异时不应直接 0 分”
    - [ ] 测试能表达“无弱项考试历史不会落成 `review_weak_topics`”
    - [ ] 测试能表达“纯空白必填槽位无法通过保存门禁”
  - Verification:
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning/test_exam_session.py -q`
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning/test_state_flow.py -q`
  - Dependencies: None
  - Files likely touched:
    - `tests/prompt_learning/test_exam_session.py`
    - `tests/prompt_learning/test_state_flow.py`
  - Estimated scope: S

## Phase 2: Fill Grading

- [ ] Task: 修复填空题对中文格式差异的评分语义
  - Description: 在不引入新依赖的前提下，先规范化答案，再用不依赖空白分词的比较逻辑完成 exact / partial / wrong 三档判断。
  - Acceptance:
    - [ ] 中文或混合语言答案因格式性空白差异不再直接判 0 分
    - [ ] 现有 range 特判和 `acceptable_variants` 分支继续有效
    - [ ] 部分得分分支仍可被触发
  - Verification:
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning/test_exam_session.py -q`
  - Dependencies: Task 1
  - Files likely touched:
    - `agent-skills/prompt-learning/scripts/exam.py`
    - `tests/prompt_learning/test_exam_session.py`
  - Estimated scope: S

- [ ] Task: 修复考试完成后无弱项时的显式推荐动作
  - Description: 调整考试历史写入路径，让 `recommended_next_action` 只在真实存在弱项时写成 `review_weak_topics`，否则写成中性动作 `open_dashboard`。
  - Acceptance:
    - [ ] 有弱项时继续写入 `review_weak_topics`
    - [ ] 无弱项时写入 `open_dashboard`
    - [ ] 首页消费显式动作时不再出现“没有弱项却推荐补弱”的矛盾
  - Verification:
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning/test_state_flow.py -q`
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning/test_exam_session.py -q`
  - Dependencies: Task 1
  - Files likely touched:
    - `agent-skills/prompt-learning/scripts/exam.py`
    - `tests/prompt_learning/test_state_flow.py`
    - `tests/prompt_learning/test_exam_session.py`
  - Estimated scope: S

## Checkpoint: After Phase 2

- [ ] 评分相关回归测试通过
- [ ] 考试状态相关回归测试通过
- [ ] CLI 输出 schema 未发生非预期变化

## Phase 3: Prompt Lab Validation

- [ ] Task: 收紧 Prompt Lab 对空槽位的定义
  - Description: 把纯空白字符串统一识别为空值，并确保 `validate_slots()` 与 `save_template()` 对该规则保持一致。
  - Acceptance:
    - [ ] `validate_slots()` 会把 `"   "` 视为空槽位
    - [ ] `save_template()` 会拒绝包含纯空白必填槽位的模板
    - [ ] 现有合法模板 fixture 仍能正常保存
  - Verification:
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning/test_state_flow.py -q`
  - Dependencies: Task 1
  - Files likely touched:
    - `agent-skills/prompt-learning/scripts/prompt_lab.py`
    - `tests/prompt_learning/test_state_flow.py`
  - Estimated scope: S

## Phase 4: Docs And Final Verification

- [ ] Task: 对齐考试与状态模型文档
  - Description: 更新考试中心和状态模型文档，明确“考试完成后只有在存在真实弱项时才推荐 `review_weak_topics`，否则回到 `open_dashboard`”。
  - Acceptance:
    - [ ] `exam-center.md` 与 `state-model.md` 描述同一条动作规则
    - [ ] 文档不再暗示考试结束必然进入补弱路径
  - Verification:
    - [ ] 文档审查
  - Dependencies: Task 3
  - Files likely touched:
    - `docs/prompt-learning-architecture/exam-center.md`
    - `docs/prompt-learning-architecture/state-model.md`
  - Estimated scope: S

- [ ] Task: 对齐 Prompt Lab 保存边界文档并完成全量回归
  - Description: 更新 Prompt Lab 文档中的空槽位定义和保存门禁描述，并完成 lint 与 prompt-learning 测试全量回归。
  - Acceptance:
    - [ ] `prompt-lab.md` 明确纯空白值属于无效槽位
    - [ ] `tests/prompt_learning` 全绿
    - [ ] `ruff check` 通过
  - Verification:
    - [ ] `.venv/bin/python -m pytest tests/prompt_learning -q`
    - [ ] `.venv/bin/ruff check agent-skills/prompt-learning/scripts tests/prompt_learning`
  - Dependencies: Task 4
  - Files likely touched:
    - `docs/prompt-learning-architecture/prompt-lab.md`
    - `tests/prompt_learning/`
    - `agent-skills/prompt-learning/scripts/`
  - Estimated scope: M

## Checkpoint: Complete

- [ ] 所有任务的 acceptance criteria 都已满足
- [ ] 相关文档、测试、实现的行为口径一致
- [ ] 变更可以进入实现阶段
