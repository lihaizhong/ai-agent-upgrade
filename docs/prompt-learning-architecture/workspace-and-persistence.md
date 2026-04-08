# Prompt Learning Workspace 与持久化设计

## 目标

为 `prompt-learning` 提供统一、克制、可扩展的持久化机制，使学习平台能够保留必要的长期信息，同时避免把 workspace 变成杂乱的对话日志目录。

## Workspace 根目录

所有持久化信息统一放在项目根目录下：

`prompt-learning-workspace/`

每个用户拥有独立空间：

`prompt-learning-workspace/<username>/`

## 用户名规则

用户目录名生成规则如下：

1. 优先读取 `git config user.name`
2. 如果用户名中包含空格，将空格替换为 `-`
3. 如果读取失败或为空，使用 `default-zoom`

示例：

- `Li Haizhong` -> `Li-Haizhong`
- `Jane` -> `Jane`
- 空值 -> `default-zoom`

## 持久化原则

### 1. 只存长期有价值的信息

允许存储：

- 学习进度
- 当前模块与当前课程摘要
- 练习结果摘要
- 错题与薄弱点
- 考试历史与报告
- 用户确认保存的 prompt 模板

### 2. 不存中间过程

不保存：

- 中间推理
- 临时草稿
- 一次性题干全文
- 临时教学内容
- 冗余对话日志

### 3. 优先存摘要，不存大段正文

例如练习记录保存题目摘要和错误标签，而不是完整题面和完整答案。

## 推荐目录结构

```text
prompt-learning-workspace/
  <username>/
    profile/
      learner.json
      preferences.json
    progress/
      current-state.json
      course-progress.json
      mastery.json
    practice/
      practice-history.jsonl
      mistakes.jsonl
    exam/
      exam-history.jsonl
      reports/
    prompt-lab/
      template-index.json
      templates/
```

## 目录职责

### `profile/`

保存用户元信息与偏好。

#### `learner.json`

保存 workspace 用户基本信息：

```json
{
  "workspace_user": "Li-Haizhong",
  "source_git_username": "Li Haizhong",
  "created_at": "2026-04-08T10:00:00+08:00",
  "updated_at": "2026-04-08T10:00:00+08:00"
}
```

#### `preferences.json`

保存少量稳定偏好：

```json
{
  "use_question_tool": true,
  "preferred_module": "learning",
  "preferred_difficulty": "auto",
  "language": "zh-CN",
  "updated_at": "2026-04-08T10:00:00+08:00"
}
```

### `progress/`

保存产品态和课程进度。

#### `current-state.json`

记录当前平台上下文：

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

#### `course-progress.json`

记录课程完成情况：

```json
{
  "completed_courses": [1, 2],
  "in_progress_course": 3,
  "last_completed_course": 2,
  "course_status": {
    "1": {
      "status": "completed",
      "completed_at": "2026-04-01T20:00:00+08:00"
    },
    "3": {
      "status": "in_progress",
      "started_at": "2026-04-08T09:40:00+08:00"
    }
  },
  "updated_at": "2026-04-08T10:00:00+08:00"
}
```

#### `mastery.json`

记录课程级掌握度摘要：

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

建议的掌握度枚举：

- `new`
- `developing`
- `good`
- `strong`

### `practice/`

保存练习历史摘要和错题记录。

#### `practice-history.jsonl`

每行记录一次练习摘要：

```json
{
  "timestamp": "2026-04-08T10:10:00+08:00",
  "course_id": 3,
  "course_name": "思维链提示",
  "entry_type": "current",
  "question_type": "design",
  "result": "partial",
  "mistake_tags": ["缺少适用边界"],
  "strength_tags": ["核心概念正确"],
  "prompt_summary": "为解释数学解题过程设计思维链提示",
  "feedback_summary": "知道作用，但结构还不稳定"
}
```

#### `mistakes.jsonl`

每行记录一个待回练错误模式：

```json
{
  "timestamp": "2026-04-08T10:10:00+08:00",
  "course_id": 3,
  "course_name": "思维链提示",
  "mistake_tag": "缺少适用边界",
  "mistake_summary": "会描述技术原理，但不会说明什么时候不该用",
  "source": "practice",
  "status": "open",
  "review_count": 0,
  "last_reviewed_at": null
}
```

建议状态枚举：

- `open`
- `reviewing`
- `resolved`

### `exam/`

保存考试摘要和详细报告。

#### `exam-history.jsonl`

```json
{
  "timestamp": "2026-04-08T11:00:00+08:00",
  "exam_type": "diagnostic",
  "score": 72,
  "total_score": 100,
  "weak_courses": [3, 7],
  "weak_topics": ["思维链结构化表达", "检索增强边界判断"],
  "report_path": "exam/reports/2026-04-08-diagnostic.md"
}
```

#### `reports/`

保存详细报告 Markdown 文件，例如：

- `2026-04-08-diagnostic.md`
- `2026-04-08-final.md`

### `prompt-lab/`

保存用户明确确认的模板成果。

#### `template-index.json`

```json
{
  "templates": [
    {
      "id": "tpl-20260408-001",
      "name": "会议纪要总结器",
      "topic": "会议纪要总结",
      "created_at": "2026-04-08T12:00:00+08:00",
      "updated_at": "2026-04-08T12:00:00+08:00",
      "path": "prompt-lab/templates/tpl-20260408-001.json",
      "tags": ["summary", "work"]
    }
  ],
  "updated_at": "2026-04-08T12:00:00+08:00"
}
```

#### `templates/<id>.json`

```json
{
  "id": "tpl-20260408-001",
  "name": "会议纪要总结器",
  "topic": "会议纪要总结",
  "slots": {
    "task": "总结会议纪要并提取行动项",
    "input": "会议记录文本",
    "output_format": "Markdown 列表",
    "constraints": "只基于输入内容，不编造未提及事项",
    "quality_bar": "行动项明确、责任人清楚、结构稳定"
  },
  "prompt": "你是一名专业会议助理...",
  "notes": "适合周会纪要整理",
  "created_at": "2026-04-08T12:00:00+08:00",
  "updated_at": "2026-04-08T12:00:00+08:00"
}
```

## 数据格式选择原则

### JSON

用于当前态和索引数据：

- 适合覆盖写
- 便于按键读取
- 适合首页与状态读取

### JSONL

用于历史事件流：

- 便于追加
- 适合练习和考试日志
- 后续容易做聚合与回放

## 最小可落地文件集

V1 最少需要这些文件：

- `profile/learner.json`
- `profile/preferences.json`
- `progress/current-state.json`
- `progress/course-progress.json`
- `progress/mastery.json`
- `prompt-lab/template-index.json`

以下文件可按首次写入时创建：

- `practice/practice-history.jsonl`
- `practice/mistakes.jsonl`
- `exam/exam-history.jsonl`

## 推荐逻辑的数据来源

首页与学习档案的推荐主要基于以下文件：

- `current-state.json`
- `course-progress.json`
- `mastery.json`
- `mistakes.jsonl`
- `exam-history.jsonl`
- `template-index.json`

因此 workspace 不是单纯存档，而是平台推荐与恢复能力的基础。

## 不做的事情

V1 暂不设计：

- 全量对话归档
- 临时草稿历史版本链
- 复杂评分数据库
- 自动聚类和知识图谱

先保证结构稳定、内容克制、后续可扩展。
