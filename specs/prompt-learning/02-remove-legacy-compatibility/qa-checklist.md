# QA Checklist: Prompt Learning Platform

## Execution Status

- Status: Executed
- Executed at: 2026-04-08
- Result: Core platform QA passed
- Notes:
  - Platform command surface, persistence flows, and legacy removal checks passed.
  - QA used isolated workspace users for persistence scenarios.
  - One earlier manual verification report remains in the real learner workspace and was not deleted automatically.

## Purpose

This checklist validates that `prompt-learning` now behaves as a platform-only product surface after legacy compatibility removal.

## Environment

- Repo root: `/Users/lihaizhong/Documents/Project/ai-agent-upgrade`
- Skill root: `.opencode/skills/prompt-learning`
- Python: `/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python`

## 1. Lint

- [x] Run:

```bash
ruff check .opencode/skills/prompt-learning/scripts
```

Expected:

- no lint errors

## 2. Command Surface

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts --help
```

Expected:

- help output contains only:
  - `workspace`
  - `home`
  - `learning`
  - `practice`
  - `exam`
  - `lab`
  - `profile`
- help output does not contain:
  - `mode`
  - `learn`
  - `generate`
  - `state`

## 3. Home

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts home --dashboard
```

Expected:

- returns JSON
- includes:
  - `current`
  - `resume`
  - `recommendation`
  - `cards`
  - `question`

## 4. Learning

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learning --catalog
```

Expected:

- returns course categories
- includes categories such as:
  - `基础课程`
  - `推理课程`
  - `知识课程`

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learning --lesson-meta --course 3 --username qa-learning-test
```

Expected:

- returns `course_id`, `course_name`, `file_path`
- writes:
  - `prompt-learning-workspace/qa-learning-test/progress/current-state.json`
  - `prompt-learning-workspace/qa-learning-test/progress/course-progress.json`
- state shows:
  - `current_module = learning`
  - `current_course_id = 3`

- [x] Completed-course reopen check:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learning --complete --course 3 --username qa-learning-reopen-test
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts learning --lesson-meta --course 3 --username qa-learning-reopen-test
```

Expected:

- `course-progress.json` still shows course `3` as `completed`
- reopening a completed course does not reset it to `in_progress`

## 5. Practice

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts practice --entry-points
```

Expected:

- includes:
  - `当前课程继续练`
  - `专项练习`
  - `错题回练`

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts practice --blueprint --mode targeted --course 3
```

Expected:

- includes:
  - `mode`
  - `goal`
  - `constraints`
  - `response_schema`

- [x] Record result:

```bash
cd .opencode/skills/prompt-learning
printf '%s' '{"course_id":3,"entry_type":"targeted","question_type":"diagnose","result":"partial","mistake_tags":["缺少适用边界"],"strength_tags":["核心概念正确"],"prompt_summary":"思维链练习","feedback_summary":"需要补充边界说明"}' | /Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts practice --record-result --username qa-practice-test
```

Expected:

- writes:
  - `practice/practice-history.jsonl`
  - `practice/mistakes.jsonl`
  - `progress/mastery.json`
  - `progress/current-state.json`
- does not persist full draft content or chain-of-thought

## 6. Exam

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --entry-points
```

Expected:

- includes:
  - `诊断考试`
  - `综合考试`

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --structure --type diagnostic
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --blueprint --type final
```

Expected:

- structure and blueprint remain stable
- total score is `100`

- [x] Record exam history:

```bash
cd .opencode/skills/prompt-learning
printf '%s' '{"exam_type":"diagnostic","score":72,"total_score":100,"weak_courses":[3,7],"weak_topics":["思维链结构化表达","检索增强边界判断"],"report_path":"prompt-learning-workspace/qa-exam-test/exam/reports/sample.md"}' | /Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --record-history --username qa-exam-test
```

Expected:

- writes `exam/exam-history.jsonl`

- [x] Report path check:

```bash
cd .opencode/skills/prompt-learning
printf '[]' | /Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts exam --report --username qa-exam-report-test
```

Expected:

- report path is under:
  - `prompt-learning-workspace/qa-exam-report-test/exam/reports/`
- not under repository root `exam-result/`

## 7. Prompt Lab

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts lab --workflow --topic "会议纪要总结"
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts lab --interview-blueprint --topic "会议纪要总结"
```

Expected:

- returns workflow and slot blueprint

- [x] Save template:

```bash
cd .opencode/skills/prompt-learning
printf '%s' '{"name":"会议纪要总结器","topic":"会议纪要总结","slots":{"task":"总结会议纪要","input":"会议记录文本","output_format":"Markdown 列表","constraints":"不要编造","quality_bar":"结构稳定"},"prompt":"你是一名会议助理...","notes":"QA template"}' | /Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts lab --save-template --username qa-lab-test
```

Expected:

- writes:
  - `prompt-lab/template-index.json`
  - `prompt-lab/templates/*.json`
- only confirmed templates are persisted

## 8. Profile

- [x] Run:

```bash
cd .opencode/skills/prompt-learning
/Users/lihaizhong/Documents/Project/ai-agent-upgrade/.venv/bin/python -m scripts profile --summary --username qa-lab-test
```

Expected:

- includes:
  - `current`
  - `progress`
  - `mastery`
  - `mistakes`
  - `exams`
  - `templates`

## 9. Legacy Removal Search

- [x] Run:

```bash
rg "PromptLearningEngine|from \\.engine import|import PromptLearningEngine" .opencode/skills/prompt-learning
```

Expected:

- no active code matches

- [x] Run:

```bash
rg "mode|learn --|generate --|state --" .opencode/skills/prompt-learning/SKILL.md .opencode/skills/prompt-learning/reference .opencode/skills/prompt-learning/agents .opencode/skills/prompt-learning/evals
```

Expected:

- no active user-facing guidance still presents old commands as supported usage

## 10. QA Notes

- Record any failures with:
  - command
  - expected behavior
  - actual behavior
  - affected file or module
- Use isolated test usernames where persistence is involved.
- Do not use the real learner workspace for destructive or noisy QA data unless explicitly intended.
