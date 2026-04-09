# Implementation Plan: 考试题目存储与提交流程优化

## 概述

根因：LLM 需要拼装完整 question 对象提交答案，多次尝试才成功。
解决：新增 submit_question 存储题目，submit_answer 不再接收 question；essay 题型继续允许传 rubric_scores，避免破坏现有大题评分。

---

## Slice 1: submit_question 方法 ✅

### 改动
- `agent-skills/prompt-learning/scripts/exam.py` 新增 `ExamService.submit_question()`

### 逻辑
1. 校验 session 存在且进行中
2. 校验 question 对象与 slot 匹配（复用 `_validate_slot_question`）
3. 校验同一题号不可重复提交
4. 存入 `session["questions"][current_num - 1]`
5. 写入 session，返回确认信息

---

## Slice 2: CLI 入口 ✅

### 改动
- `agent-skills/prompt-learning/scripts/__main__.py` 新增 `--submit-question` 参数

### 逻辑
- 从 stdin 读取 JSON payload
- 调用 `exam_service.submit_question()`

---

## Slice 3: 简化 submit_answer ✅

### 改动
- `agent-skills/prompt-learning/scripts/exam.py` 修改 `ExamService.submit_answer()`

### 逻辑
1. 选择题和填空题接收 `{answer, question_num}` 而非 `{answer, question}`
2. 校验 question_num 与当前题匹配
3. 从 `session["questions"][current_num - 1]` 读取完整题目
4. 未存储题目时抛出明确错误
5. essay 题型允许额外接收 `rubric_scores` 并传给 `_grade_answer`
6. 不再 `session["questions"].append()`（题目已由 submit_question 写入）

---

## Slice 4: 扩展 current_question ✅

### 改动
- `agent-skills/prompt-learning/scripts/exam.py` 修改 `ExamService._session_to_context()`

### 逻辑
1. 检查 `session["questions"][current_num - 1]` 是否已存储
2. 已存储 + 选择题 → 返回 `interaction.mode: "selector"` + 选项结构
3. 已存储 + 其他题型 → 返回 `interaction.mode: "inform"` + `question_content`
4. 未存储 → 保持现有行为（`inform` + slot 元数据）

---

## Slice 5: SKILL.md 更新 ✅

### 改动
- 新增"题目生成指引"章节
- 更新脚本调用边界
- 更新题目生成流程（含 submit_question 步骤）
- 明确题目存储在会话生命周期内

### 补充
- 补充 mc/fill/essay 的结构化 JSON 示例，覆盖 `course_id`、`topic_tags`、`correct_answer`、`answer`、`scoring_rubric`
- 明确 essay 提交答案时可继续传 `rubric_scores`

---

## Slice 6: workspace 状态同步 ✅

### 改动
- 保留 `prompt-learning-workspace/lihzsky/` 下的当前考试会话与进度状态变更

### 逻辑
- 这些文件属于本次真实用户状态同步范围，不视为无关运行产物
