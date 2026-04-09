# Tasks: Prompt Learning Exam Weakness Rollup And Final Coverage

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/06-exam-weakness-rollup-and-final-coverage/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/06-exam-weakness-rollup-and-final-coverage/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Question Metadata Contract

- [ ] Task: Define optional weakness metadata on exam question payloads
  - Acceptance: 题目对象允许携带 `course_id` 和 `topic_tags`，并在会话中被保留
  - Verify: 检查 `submit_answer()` 保存后的 session 数据
  - Files: `agent-skills/prompt-learning/scripts/exam.py`

## Phase 2: Weakness Summarization

- [ ] Task: Add `_summarize_weaknesses(session)` to exam service
  - Acceptance: 方法可基于 `questions` 和 `scores` 输出非空或合理的 `weak_courses` / `weak_topics`
  - Verify: 新增或更新测试断言
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/test_exam_session.py`

- [ ] Task: Make weakness rollup deterministic and deduplicated
  - Acceptance: 同一课程或标签多次出现时，最终输出去重且顺序稳定
  - Verify: 测试重复错题或重复标签场景
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/test_exam_session.py`

## Phase 3: Finish Flow Integration

- [ ] Task: Replace hard-coded empty weakness arrays in `finish_session()`
  - Acceptance: `record_history()` 收到真实弱项结果，而不是 `[]`
  - Verify: 检查历史文件写入内容
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/test_exam_session.py`

- [ ] Task: Keep recommendation semantics aligned with history content
  - Acceptance: 结束考试后，`recommended_next_action = review_weak_topics` 时，历史里确实存在对应弱项数据
  - Verify: 联合检查历史文件与 current state
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/test_state_flow.py`, `tests/prompt_learning/test_exam_session.py`

## Phase 4: Final Coverage Completion

- [ ] Task: Refactor exam-session test helpers to support multiple exam types
  - Acceptance: 测试 helper 不再只服务 `diagnostic`
  - Verify: 测试代码审查
  - Files: `tests/prompt_learning/test_exam_session.py`

- [ ] Task: Add full `final` exam completion test
  - Acceptance: `final` 覆盖 start → submit all → finish → history/report assertions
  - Verify: `./.venv/bin/python -m unittest tests.prompt_learning.test_exam_session`
  - Files: `tests/prompt_learning/test_exam_session.py`

- [ ] Task: Keep full `diagnostic` exam completion test
  - Acceptance: 原有 `diagnostic` 完整闭环测试仍存在并继续通过
  - Verify: `./.venv/bin/python -m unittest tests.prompt_learning.test_exam_session`
  - Files: `tests/prompt_learning/test_exam_session.py`

## Verification

- [ ] Task: Run prompt-learning lint and exam-session tests
  - Acceptance: Ruff 与考试会话测试全部通过
  - Verify: 运行验证命令

- [ ] Task: Run full prompt-learning test suite
  - Acceptance: platform / state_flow / content_quality / exam_session 全通过
  - Verify: 运行完整 unittest 命令

## Global Gates

- [ ] Gate: `finish_session()` no longer writes empty weakness data by default
  - Acceptance: 除非题目本身完全缺少元数据，否则不再输出硬编码空数组
  - Verify: 代码审查 + 测试

- [ ] Gate: `final` and `diagnostic` are both proven by automated completion tests
  - Acceptance: 两种考试类型都存在完整闭环自动化覆盖
  - Verify: 测试审查 + unittest 运行结果
