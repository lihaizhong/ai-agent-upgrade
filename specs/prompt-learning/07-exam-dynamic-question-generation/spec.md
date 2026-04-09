# Spec Change: 考试题目存储与提交流程优化

## 根因

考试流程中 LLM 需要大量"拼装式交互"：

1. `current_question` 只返回 slot 元数据，LLM 必须自己编题
2. `submit_answer` 要求传入完整 question 对象（含 correct_answer、course_id、topic_tags 等），拼错任何一个字段就报错
3. 多次尝试拼装 question 对象，导致交互效率极低

## 目标

1. 将题目内容存储到 session，LLM 提交答案时不再传完整 question 对象
2. 选择题已存储时自动触发选择器
3. 报告生成和弱点分析不受影响
4. 同步 `prompt-learning-workspace/lihzsky/` 下的真实学习/考试状态数据

## 设计

### 1. 新增 `submit_question` 接口

LLM 生成题目后，先调用此接口将题目存入 session：

```json
{"question": {完整题目对象}}
```

- 校验题型/分值/难度（复用 `_validate_slot_question`）
- 同一题号不可重复提交
- 存入 `session["questions"][current_num - 1]`

### 2. 简化 `submit_answer` 接口

从 `session["questions"]` 读取题目，选择题和填空题只需传：

```json
{"answer": "B", "question_num": 3}
```

- 大题仍可传可选 `rubric_scores`，用于保留现有脚本评分逻辑：

```json
{
  "answer": "完整回答",
  "question_num": 9,
  "rubric_scores": {
    "结构完整": 6,
    "技术选择": 4.5,
    "权衡分析": 4.5
  }
}
```

- 校验题目已存储，否则报错
- 移除 `question` 参数
- `rubric_scores` 仅用于 essay 题型，不能因为接口简化导致 essay 默认为 0 分

### 3. 扩展 `current_question` 返回

- 题目已存储时：选择题返回 `interaction.mode: "selector"` + 选项结构；其他题型返回 `interaction.mode: "inform"` + 完整题目内容
- 题目未存储时：保持现有行为（返回 slot 元数据 + `inform`）

### 4. Workspace 状态同步

本次变更允许同步 `prompt-learning-workspace/lihzsky/` 下的当前考试会话与进度状态，作为真实用户学习/考试状态的一部分，不视为无关运行产物。

### 5. SKILL.md 更新

- 新增"题目生成指引"章节（mc/fill/essay 三种题型模板与结构化 JSON 字段要求）
- 更新脚本调用边界（新增 submit_question）
- 题目生成流程：先 `current_question` → 生成题目 → `submit_question` 存储 → 用户作答 → `submit_answer`
- 明确 essay 提交答案时仍可传 `rubric_scores`
- 明确题目存储在会话生命周期内，不属于"临时题干草稿"的持久化禁止范围

## 已实现改动

### exam.py
- 新增 `ExamService.submit_question()` 方法
- 修改 `ExamService.submit_answer()` → 从 session 读取题目，不再接收 question
- essay 题型继续接收并传递 `rubric_scores`，避免大题评分回归为 0 分
- 修改 `ExamService._session_to_context()` → 题目已存储时选择题返回 selector

### __main__.py
- 新增 `--submit-question` CLI 入口

### SKILL.md
- 新增"题目生成指引"章节
- 新增"题目生成流程"小节（含 submit_question 步骤）
- 更新"必须调用脚本的场景"列表
- 补充结构化 JSON 示例与 essay `rubric_scores` 提交流程

### workspace
- 同步 `prompt-learning-workspace/lihzsky/` 的当前学习/考试状态数据

## 验收标准

- [x] LLM 生成题目后可存入 session
- [x] 选择题和填空题提交答案只需传 answer + question_num
- [x] 大题提交答案可传 answer + question_num + rubric_scores，且评分逻辑不回归为 0 分
- [x] 选择题已存储时触发选择器
- [x] 报告生成和弱点分析正常工作（依赖 session["questions"]）
- [x] fill/essay 题型评分逻辑不受影响
- [x] `lihzsky` workspace 当前考试/进度状态按本次流程同步
