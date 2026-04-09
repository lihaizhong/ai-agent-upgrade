# Task Breakdown: 考试题目存储与提交流程优化

## Tasks

### Task 1: SKILL.md 题目生成指引 ✅
- 新增"题目生成指引"章节，覆盖 mc/fill/essay 三种题型
- 新增"题目生成流程"小节（含 submit_question 步骤）
- 更新脚本调用边界
- 补充结构化 JSON 示例和 essay `rubric_scores` 提交流程

### Task 2: submit_question 方法 ✅
- 新增 `ExamService.submit_question(payload, session_id)`
- 校验题型/分值/难度，存入 session["questions"]
- 同一题号不可重复提交

### Task 3: CLI 入口 submit-question ✅
- `__main__.py` 新增 `--submit-question` 参数
- 从 stdin 读取 JSON payload

### Task 4: 简化 submit_answer ✅
- 选择题和填空题只接收 `{answer, question_num}`
- essay 题型允许额外接收 `rubric_scores`
- 从 session["questions"] 读取完整题目
- 未存储题目时抛出明确错误
- 不再接收完整 `question` 对象

### Task 5: 扩展 current_question ✅
- 题目已存储时：选择题返回 selector interaction，其他题型返回 inform + 完整题目
- 题目未存储时：保持现有行为

### Task 6: lihzsky workspace 状态同步 ✅
- 保留 `prompt-learning-workspace/lihzsky/` 下当前考试会话与进度状态数据
- 这些数据属于本次需求范围，不视为无关运行产物
