# Prompt Learning 状态模型设计

## 目标

为 `prompt-learning` 提供统一、可解释、可持久化的状态模型，使平台能够：

- 恢复用户上次进度
- 推荐下一步动作
- 支持学习、练习、考试、Prompt Lab 之间切换
- 将长期状态与临时会话解耦

## 设计原则

### 1. 产品态优先

状态模型首先服务于学习平台，而不是服务于某个单独脚本命令。

### 2. 当前态与历史态分离

当前状态用于恢复与导航；历史记录用于分析与推荐。不要把所有历史挤进单个状态文件。

### 3. 存摘要，不存中间过程

状态用于表达“当前在哪里、接下来做什么”，不用于保存中间推理和冗长上下文。

### 4. 推荐可解释

任何推荐动作都应可追溯到已有状态，而不是由 agent 临时编造。

## 状态层次

建议将状态分成两层：

### 一层：当前产品态

表示用户此刻处于哪个模块、哪个课程、最近完成了什么，以及下一步建议什么。

持久化文件：

- `progress/current-state.json`

### 二层：长期进度态

表示课程完成情况、掌握度、练习和考试回流的长期结果。

持久化文件：

- `progress/course-progress.json`
- `progress/mastery.json`

历史事件另存于：

- `practice/practice-history.jsonl`
- `practice/mistakes.jsonl`
- `exam/exam-history.jsonl`

## 当前产品态

### 文件

`progress/current-state.json`

### 职责

- 首页 resume
- 首页推荐动作
- 模块切换时恢复上下文
- 显示当前课程或当前模块

### 建议结构

```json
{
  "current_module": "learning",
  "current_course_id": 3,
  "current_course_name": "思维链提示",
  "last_action": "lesson_completed_waiting_practice",
  "recommended_next_action": "start_practice",
  "updated_at": "2026-04-08T10:00:00+08:00"
}
```

### 字段说明

- `current_module`
  当前所在模块，建议枚举：
  - `home`
  - `learning`
  - `practice`
  - `exam`
  - `lab`
  - `profile`

- `current_course_id`
  当前相关课程编号。无课程上下文时可为空。

- `current_course_name`
  当前课程名称，方便直接展示。

- `last_action`
  最近完成的关键动作，用于 resume 和推荐。

- `recommended_next_action`
  基于当前状态计算出的推荐动作键。

- `updated_at`
  最近更新时间。

## 长期进度态

### 课程进度

文件：

`progress/course-progress.json`

职责：

- 标识课程是否完成
- 标识当前是否存在进行中的课程
- 记录最近完成的课程

建议结构：

```json
{
  "completed_courses": [1, 2],
  "in_progress_course": 3,
  "last_completed_course": 2,
  "course_status": {
    "1": {
      "status": "completed",
      "started_at": "2026-04-01T19:00:00+08:00",
      "completed_at": "2026-04-01T20:00:00+08:00"
    },
    "3": {
      "status": "in_progress",
      "started_at": "2026-04-08T09:40:00+08:00",
      "completed_at": null
    }
  },
  "updated_at": "2026-04-08T10:00:00+08:00"
}
```

### 掌握度

文件：

`progress/mastery.json`

职责：

- 聚合课程级练习结果
- 为练习推荐和考试建议提供依据
- 为学习档案提供摘要

建议结构：

```json
{
  "courses": {
    "3": {
      "level": "developing",
      "practice_attempts": 2,
      "mistake_count": 3,
      "last_practiced_at": "2026-04-08T10:20:00+08:00"
    }
  },
  "updated_at": "2026-04-08T10:20:00+08:00"
}
```

### 掌握度等级

建议使用以下简单枚举：

- `new`
- `developing`
- `good`
- `strong`

优先追求稳定和可解释，不在 V1 引入复杂分数模型。

## 状态流转

### 首页进入学习中心

1. `current_module = home`
2. 用户选择学习
3. 更新：
   - `current_module = learning`
   - `current_course_id = <N>`
   - `last_action = lesson_started`

### 学习结束进入课后练习

课程讲授完成后更新：

- `current_module = learning`
- `last_action = lesson_completed_waiting_practice`
- `recommended_next_action = start_practice`

### 练习完成

练习结果写入历史后更新：

- `current_module = practice`
- `last_action = practice_completed`
- 根据结果决定 `recommended_next_action`

如果是当前课程课后练习，一般推荐：

- `lesson_panel`
- `practice_again`
- `review_mistakes`

### 课程完成

当用户完成课程时更新：

- `course-progress.json`
- `current-state.json`

通常同步设置：

- `last_action = course_completed`
- `recommended_next_action = continue_learning` 或 `start_practice`

### 考试完成

考试结果写入后更新：

- `current_module = exam`
- `last_action = exam_completed`
- `recommended_next_action = review_weak_topics`

### 保存模板后

Prompt Lab 完成并保存模板后更新：

- `current_module = lab`
- `last_action = template_saved`
- `recommended_next_action = open_dashboard` 或 `continue_lab`

## 推荐动作模型

推荐动作应固定在一小组可解释枚举中：

- `open_dashboard`
- `continue_learning`
- `start_practice`
- `review_mistakes`
- `take_exam`
- `open_lab`
- `review_weak_topics`

推荐本身不需要存大量说明，但应能由上层服务生成带理由的解释。

## 推荐优先级建议

V1 先采用简单规则：

1. 课程已讲完但尚未练习 -> `start_practice`
2. 有进行中的课程 -> `continue_learning`
3. 存在未解决错题 -> `review_mistakes`
4. 最近完成多门课程但未考试 -> `take_exam`
5. 默认 -> `open_dashboard`

## 状态与历史记录的关系

### 状态文件

负责回答：

- 现在在哪
- 最近做了什么
- 下一步建议什么

### 历史记录文件

负责回答：

- 练过什么
- 错过什么
- 考过什么
- 保存过什么

不要让 `current-state.json` 承担历史日志职责。

## 与模块的职责边界

### `workspace.py`

不理解学习流程，只负责路径和文件初始化。

### `state.py`

负责：

- 读取和写入当前态
- 读取和写入课程进度
- 读取和写入掌握度

不负责：

- 错题事件明细
- 考试历史明细
- Prompt Lab 模板列表

### `practice.py`

负责写练习历史与错题事件，再调用 `state.py` 更新掌握度摘要。

### `exam.py`

负责写考试历史，再让上层服务基于结果更新推荐动作。

### `profile.py`

负责聚合读取，不直接承担底层状态写入。

## 最小实现范围

V1 至少实现以下状态能力：

- 初始化默认状态文件
- 更新当前模块
- 启动课程
- 完成课程
- 记录练习结果并更新掌握度
- 从状态中生成首页 resume 所需摘要

## 不做的事情

V1 暂不引入：

- 复杂 FSM 引擎
- 多会话并行状态
- 逐题级别细粒度上下文恢复
- 学习行为预测模型

先用简单、稳定、可解释的状态模型支撑平台产品化。
