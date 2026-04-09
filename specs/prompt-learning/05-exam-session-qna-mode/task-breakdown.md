# Tasks: Prompt Learning Exam Session Q&A Mode

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/05-exam-session-qna-mode/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/05-exam-session-qna-mode/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Session Model and Persistence

- [ ] Task: Define exam session schema and storage location
  - Acceptance: `prompt-learning-workspace/<username>/exam/` 下存在清晰的进行中会话存储约定，字段覆盖 `session_id`、`status`、`current_question_num`、`answers`、`scores`、时间戳
  - Verify: 检查 `exam.py` / `workspace.py` 相关实现与输出
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `agent-skills/prompt-learning/scripts/workspace.py`

- [ ] Task: Enforce single in-progress session per user
  - Acceptance: 同一用户启动新考试时，若已有 `in_progress` 会话，脚本不会静默创建第二个会话
  - Verify: 新增测试覆盖重复启动场景
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/`

## Phase 2: ExamService Session API

- [ ] Task: Add session lifecycle methods to exam service layer
  - Acceptance: 服务层支持 `start`, `resume`, `submit`, `abandon`, `finish`
  - Verify: 通过单元测试或集成测试覆盖会话生命周期
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/`

- [ ] Task: Lock submitted questions and prevent backward navigation
  - Acceptance: 提交某题后无法再次获取该题作为可编辑当前题，上一题不可回看
  - Verify: 测试提交第 N 题后只能继续第 N+1 题
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/`

## Phase 3: CLI Surface

- [ ] Task: Add CLI commands or flags for session operations
  - Acceptance: CLI 能覆盖创建、查询当前题、提交答案、恢复、放弃、完成考试
  - Verify: 逐一运行新命令并检查 JSON 输出
  - Files: `agent-skills/prompt-learning/scripts/__main__.py`, `agent-skills/prompt-learning/scripts/exam.py`

- [ ] Task: Return selector interaction for resume-or-abandon choice
  - Acceptance: 当存在未完成会话时，脚本输出 `interaction.mode == "selector"`，选项至少包含“恢复考试”和“放弃考试”
  - Verify: 运行恢复入口命令检查 `question` 结构
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `agent-skills/prompt-learning/scripts/__main__.py`

- [ ] Task: Keep current-question and final-report outputs in inform mode
  - Acceptance: 当前题展示和终局报告输出都标记为 `interaction.mode == "inform"`
  - Verify: 检查命令输出
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `agent-skills/prompt-learning/scripts/__main__.py`

## Phase 4: Report and History Integration

- [ ] Task: Write formal exam history only on completed sessions
  - Acceptance: `completed` 会话进入 `exam-history.jsonl`，`abandoned` 会话不写正式成绩
  - Verify: 检查历史文件与状态文件
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/`

- [ ] Task: Generate end-of-exam report without mid-exam feedback leakage
  - Acceptance: 考试过程中提交答案不返回对错和得分；完成时统一生成报告
  - Verify: 测试提交答案输出与 finish 输出差异
  - Files: `agent-skills/prompt-learning/scripts/exam.py`, `tests/prompt_learning/`

## Phase 5: Docs and Skill Guidance

- [ ] Task: Update exam mode reference for session-based Q&A flow
  - Acceptance: `reference/exam-mode.md` 明确逐题、不可回看、无即时反馈、可恢复或放弃
  - Verify: 文档审查
  - Files: `agent-skills/prompt-learning/reference/exam-mode.md`

- [ ] Task: Align architecture docs and skill guidance with session model
  - Acceptance: 架构文档和 skill 描述不再暗示整卷一次性展示或即时反馈
  - Verify: 搜索相关措辞并审查
  - Files: `docs/prompt-learning-architecture/exam-center.md`, `agent-skills/prompt-learning/SKILL.md`

## Phase 6: Verification

- [ ] Task: Add automated tests for diagnostic and final session flows
  - Acceptance: 两种考试类型都覆盖启动、逐题推进、完成考试的测试
  - Verify: `./.venv/bin/python -m unittest ...`
  - Files: `tests/prompt_learning/`

- [ ] Task: Add automated tests for resume and abandon branches
  - Acceptance: 中断后能恢复当前题，放弃后不会进入正式历史
  - Verify: `./.venv/bin/python -m unittest ...`
  - Files: `tests/prompt_learning/`

- [ ] Task: Run lint and prompt-learning test suite
  - Acceptance: Ruff 通过，相关单测通过
  - Verify: `./.venv/bin/ruff check ...` 与 `./.venv/bin/python -m unittest ...`

## Global Gates

- [ ] Gate: No exam session implementation stores full paper text as long-term history by default
  - Acceptance: 会话持久化遵守 workspace 克制持久化原则
  - Verify: 审查状态 schema 和写盘逻辑

- [ ] Gate: LLM is no longer responsible for remembering exam progress
  - Acceptance: 当前题、恢复入口、完成状态都可由脚本确定返回
  - Verify: 手动走查 CLI 流程
