# Plan: Prompt Learning Exam Session Q&A Mode

## Status

- Status: Proposed
- Created: 2026-04-09
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/05-exam-session-qna-mode/spec.md)

## Source of Truth

This plan is derived from:

- [05-exam-session-qna-mode spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/05-exam-session-qna-mode/spec.md)
- [docs/prompt-learning-architecture/exam-center.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/exam-center.md)
- [docs/prompt-learning-architecture/workspace-and-persistence.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/workspace-and-persistence.md)
- [agent-skills/prompt-learning/scripts/exam.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/prompt-learning/scripts/exam.py)
- [agent-skills/prompt-learning/scripts/__main__.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/prompt-learning/scripts/__main__.py)

## Objective

在不改变现有考试蓝图、题型和分值的前提下，为 `prompt-learning` 考试中心增加逐题 Q&A 会话层，支持：

- `diagnostic` / `final` 统一逐题模式
- 提交即锁定、不可回看
- 无即时反馈
- 终局统一报告
- 中断后恢复或放弃

## Implementation Strategy

采用“先补会话状态，再补 CLI 能力，最后补文档和验证”的顺序。

原则：

1. 不推翻现有 `ExamEngine` 的蓝图、校验、评分、报告能力
2. 新增一层会话编排，而不是把状态管理继续留给 LLM
3. 会话持久化只保存最小必要信息，不把整卷全文当成长期档案

## Phase 1: Session Model and Persistence

Scope:

- 在 `exam/` workspace 下新增进行中会话存储模型
- 定义 `session_id`、`status`、`current_question_num`、`answers`、`scores` 等字段
- 建立“同一用户最多一个 `in_progress` 会话”的约束
- 明确 `completed` / `abandoned` 状态及其持久化行为

Expected outcome:

- 脚本可创建、读取、更新、放弃一个考试会话
- 会话状态对中断恢复足够稳定

## Phase 2: ExamService Session API

Scope:

- 在 `exam.py` 中新增会话级服务方法，例如：
  - `start_session()`
  - `get_in_progress_session()`
  - `get_current_question_context()`
  - `submit_answer()`
  - `abandon_session()`
  - `finish_session()`
- 保持已有 `record_history()` 和 `get_history_summary()` 职责不变

Why this phase:

先在 Python 服务层定清会话职责，再暴露到 CLI；这样命令层不会先长出一堆分散逻辑。

## Phase 3: CLI Surface in `__main__.py`

Scope:

- 为 `exam` 子命令新增会话相关参数
- 暴露恢复、放弃、当前题、提交答案、完成考试的 CLI 行为
- 为“恢复 / 放弃”输出设计 `interaction.mode == "selector"`
- 为当前题、终局报告保持 `interaction.mode == "inform"`

Expected outcome:

- LLM 不需要靠对话记住考试进度，而是通过 CLI 获取确定状态

## Phase 4: Report and History Integration

Scope:

- 让 `finish_session()` 汇总全部答案并调用既有评分 / 报告逻辑
- 仅在 `completed` 时写正式考试历史
- `abandoned` 会话不写正式成绩，但可保留最小状态记录

Key decision:

- 放弃记录与正式成绩分开，避免污染学习档案

## Phase 5: Prompt Learning Guidance and Docs

Scope:

- 更新 `reference/exam-mode.md`
- 视需要补充 `docs/prompt-learning-architecture/exam-center.md`
- 在 `SKILL.md` 中强调考试场景不提供即时反馈、必须遵守恢复/放弃优先规则

Expected outcome:

- 产品文档、skill 行为和脚本能力一致

## Phase 6: Verification

Scope:

- 为考试会话新增单元/集成测试
- 验证 `diagnostic` 和 `final` 都走逐题模式
- 验证同一用户只能有一个进行中会话
- 验证提交后不可回看
- 验证恢复 / 放弃分支
- 验证 `abandoned` 不进入正式考试历史

## Verification Commands

```bash
./.venv/bin/ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```

```bash
./.venv/bin/python -m unittest tests.prompt_learning.test_platform
./.venv/bin/python -m unittest tests.prompt_learning.test_state_flow
```

如新增独立测试文件，补充：

```bash
./.venv/bin/python -m unittest tests.prompt_learning.test_exam_session
```

## Risks

1. **会话文件与历史文件边界不清**：通过显式区分 `in_progress` / `completed` / `abandoned` 来缓解
2. **恢复逻辑依赖当前题内容**：通过只缓存进行中会话所需的当前题数据来缓解，而不是把整卷全文长期持久化
3. **CLI 过度膨胀**：通过先在服务层收敛能力边界，再决定最终命令形态来缓解
4. **测试覆盖不足**：通过给 session 生命周期补专门测试来缓解
