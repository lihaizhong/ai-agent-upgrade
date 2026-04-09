# Spec: Prompt Learning Exam Weakness Rollup And Final Coverage

## 前置依赖

1. `05-exam-session-qna-mode` 已将考试中心切到逐题 Q&A 会话模式
2. 当前 `exam` 模块已经支持 `start / current-question / submit-answer / resume / abandon / finish`
3. 当前考试完成路径已经能生成报告并写正式考试历史，但存在弱项回流缺失与测试覆盖不完整的问题

## 问题陈述

`05` 号规格完成后，考试中心的主流程已经能跑通，但还存在两个明确缺口：

### 1. 终局历史缺少真实弱项数据

当前 `finish_session()` 调用 `record_history()` 时，固定写入：

- `weak_courses = []`
- `weak_topics = []`

但 `record_history()` 仍会将：

- `last_action = exam_completed`
- `recommended_next_action = review_weak_topics`

写入当前平台状态。

这导致产品语义断裂：

- 考试已结束
- 平台推荐用户回看“薄弱点”
- 但正式考试历史里并没有真实的薄弱课程和薄弱主题

### 2. `final` 考试缺少完整闭环测试

当前新增的考试会话测试已经覆盖：

- 启动考试
- 阻止重复开始
- 当前题查询
- 放弃考试
- `diagnostic` 的提交流程和 finish 流程

但没有完整验证 `final` 考试的闭环：

- 启动 `final`
- 逐题提交
- 完成考试
- 写入历史
- 生成报告

这意味着规格虽然要求 `diagnostic` 和 `final` 都进入逐题模式，但自动化验证只证明了其中一种。

## 目标

本规格只解决这两个问题：

1. 让考试完成路径能输出真实、可解释的 `weak_courses` 和 `weak_topics`
2. 补齐 `final` 考试的完整自动化闭环测试

## 非目标

本规格不包括：

- 重写考试会话模型
- 更改题数、题型、分值或题位蓝图
- 引入自适应考试
- 解决“恢复时必须还原同一道未提交题目”的问题
- 建立复杂的 AI 弱项分析系统
- 将弱项分析扩展为完整知识诊断引擎

## 核心决策

### 1. 弱项回流先做“规则版”，不做复杂推断

目标不是一次把弱项分析做得很聪明，而是先把产品闭环打通。

因此本规格采用“轻量、稳定、可解释”的规则：

- 某题未得满分，则该题关联的课程和主题进入弱项候选
- 最终对候选值去重，输出 `weak_courses` 和 `weak_topics`

### 2. 题目元数据增加弱项映射信息

要汇总弱项，单靠题位摘要不够。

题目对象应允许携带以下元数据：

- `course_id`
- `topic_tags`

示例：

```json
{
  "type": "mc",
  "num": 3,
  "difficulty": "中级",
  "question": "……",
  "course_id": 4,
  "topic_tags": ["clarity", "selection"],
  "options": [...],
  "correct_answer": "B",
  "score": 5
}
```

这两个字段在本次 change 中建议为可选字段，而不是强制必填，避免把所有现有题目生成逻辑一次性打断。

### 3. `finish_session()` 必须输出真实弱项结果

`finish_session()` 在生成报告后，必须基于本次考试题目与得分汇总弱项，再写入正式历史。

它不应继续写死空数组。

### 4. `final` 测试必须与 `diagnostic` 对等

`final` 不再只验证“能不能开始”，而要验证完整完成路径。

## 设计方案

### A. 弱项汇总接口

在 `ExamService` 中新增内部方法，例如：

```python
def _summarize_weaknesses(self, session: dict) -> dict:
    return {
        "weak_courses": [3, 7],
        "weak_topics": ["clarity", "boundary"]
    }
```

### B. 弱项汇总规则

对 `session["questions"]`、`session["scores"]` 逐题处理：

- 若该题得分小于题目满分：
  - 读取 `question["course_id"]`
  - 读取 `question["topic_tags"]`
  - 将其加入候选列表

汇总后：

- `weak_courses`：按出现顺序去重后的课程 ID 列表
- `weak_topics`：按出现顺序去重后的主题标签列表

### C. 大题的处理

大题先不做复杂自然语言解析。

本次 change 保持简单：

- 大题同样通过 `course_id` 和 `topic_tags` 提供弱项映射
- 若大题未得满分，则这些 tags 进入弱项候选

后续如果需要，再单独做更细颗粒度的 rubric 到 topic 的映射。

### D. 测试结构调整

将现有 `diagnostic` 完整流程 helper 抽象成更通用的方法，例如：

- `_complete_exam(session_id, exam_type)`
- `_assert_finished_exam(...)`

并补充：

- `test_finish_diagnostic_session_generates_report_and_history`
- `test_finish_final_session_generates_report_and_history`

若实现了弱项回流，测试还应验证：

- `weak_courses` 不为空或符合预期
- `weak_topics` 不为空或符合预期

## 成功标准

本规格完成当且仅当：

1. `finish_session()` 不再向 `record_history()` 传递固定空数组弱项
2. 完成后的考试历史包含真实生成的 `weak_courses` 和 `weak_topics`
3. `recommended_next_action = review_weak_topics` 与历史中的弱项数据保持一致
4. `diagnostic` 和 `final` 都有完整的自动化完成路径测试
5. 新测试能验证报告生成、历史写入以及考试类型正确性

## 风险

1. **题目元数据缺失**：如果生成的题目没有 `course_id` 和 `topic_tags`，弱项汇总仍可能为空
2. **规则过粗**：未得满分即记弱项会比较保守，但它至少是稳定且可解释的
3. **测试 helper 过度耦合**：如果测试把太多实现细节写死，后续演进会增加维护成本

## 开放问题

1. 当题目缺少 `course_id` 或 `topic_tags` 时，是直接跳过，还是记录为未知弱项？本规格倾向于先跳过，不发明未知标签
2. 是否需要给 `weak_topics` 加数量上限？MVP 中先不限制，等真实数据量出现后再收敛
