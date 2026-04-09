# Plan: Prompt Learning Exam Weakness Rollup And Final Coverage

## Status

- Status: Proposed
- Created: 2026-04-09
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/06-exam-weakness-rollup-and-final-coverage/spec.md)

## Source of Truth

This plan is derived from:

- [05-exam-session-qna-mode spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/05-exam-session-qna-mode/spec.md)
- [06-exam-weakness-rollup-and-final-coverage spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/06-exam-weakness-rollup-and-final-coverage/spec.md)
- [agent-skills/prompt-learning/scripts/exam.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/prompt-learning/scripts/exam.py)
- [tests/prompt_learning/test_exam_session.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/tests/prompt_learning/test_exam_session.py)

## Objective

在不重写考试会话模型的前提下：

- 为考试完成链路补上真实弱项回流
- 为 `final` 考试补齐完整自动化闭环测试

## Implementation Strategy

采用最小增量策略：

1. 先给题目对象补弱项映射元数据约定
2. 再实现规则版 `_summarize_weaknesses(session)`
3. 再把 `finish_session()` 接到真实弱项输出
4. 最后整理并补齐 `diagnostic` / `final` 的完整会话测试

## Phase 1: Question Metadata Contract

Scope:

- 明确题目对象可选支持：
  - `course_id`
  - `topic_tags`
- 让 `submit_answer()` 在保存题目时保留这两个字段
- 如有必要，补文档说明这两个字段用于终局弱项回流

Expected outcome:

- 会话内保存的题目足以支持后续弱项汇总

## Phase 2: Weakness Summarization

Scope:

- 在 `ExamService` 中新增 `_summarize_weaknesses(session)`
- 按“未得满分即记弱项候选”的规则汇总：
  - `weak_courses`
  - `weak_topics`
- 保证输出去重、顺序稳定

Expected outcome:

- 从会话数据中稳定推导出基础弱项信息

## Phase 3: Finish Flow Integration

Scope:

- 修改 `finish_session()`
- 用 `_summarize_weaknesses(session)` 的结果替换当前写死的空数组
- 保证正式考试历史、当前平台状态、推荐动作三者语义一致

Expected outcome:

- 结束考试后，历史和推荐动作指向真实弱项

## Phase 4: Test Coverage Completion

Scope:

- 重构现有测试 helper，避免重复代码
- 保留 `diagnostic` 完整闭环测试
- 新增 `final` 完整闭环测试
- 补充对 `weak_courses` / `weak_topics` 的断言

Expected outcome:

- 两种考试类型都被自动化证明能跑完整闭环

## Verification Commands

```bash
./.venv/bin/ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```

```bash
./.venv/bin/python -m unittest tests.prompt_learning.test_exam_session
```

```bash
./.venv/bin/python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_state_flow tests.prompt_learning.test_content_quality tests.prompt_learning.test_exam_session
```

## Risks

1. **题目元数据接入不完整**：如果测试里补了元数据，但真实题目生成链路没跟上，线上仍会出现空弱项
2. **规则过于粗糙**：先接受这个限制，优先完成产品闭环
3. **测试重构破坏现有可读性**：通过保持 helper 简单、命名清晰来控制
