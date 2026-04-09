# RAG Learning 状态模型设计

## 目标

为 `rag-learning` 提供统一、可解释、可持久化的状态模型，使平台能够：

- 恢复用户上次进度
- 推荐下一步动作
- 支持学习、实战、实验、评审之间切换
- 将长期状态与临时会话解耦

## 设计原则

### 1. 产品态优先

状态模型首先服务于平台导航与训练连续性，而不是服务于某个单独脚本命令。

### 2. 当前态与历史态分离

当前状态用于恢复与导航；历史记录用于分析与推荐。不要把实验历史和方案历史塞进单个状态文件。

### 3. 存摘要，不存中间过程

状态用于表达“当前在哪里、接下来做什么”，不用于保存长篇对话和过程推理。

### 4. 推荐可解释

任何推荐动作都应可追溯到已有状态，而不是由 agent 临时编造。

## 状态层次

建议将状态分成三层：

### 一层：当前产品态

表示用户此刻处于哪个模块、关联哪个课程或项目、最近完成了什么，以及下一步建议什么。

持久化文件：

- `progress/current-state.json`

### 二层：长期进度态

表示课程完成情况、项目推进情况与能力摘要。

持久化文件：

- `progress/course-progress.json`
- `progress/build-progress.json`
- `progress/competency.json`

### 三层：历史事件

另存于：

- `lab/experiment-history.jsonl`
- `review/review-history.jsonl`

## 当前产品态

### 文件

`progress/current-state.json`

### 职责

- 首页 resume
- 首页推荐动作
- 模块切换时恢复上下文
- 显示当前课程、当前项目或当前实验

### 建议结构

```json
{
  "current_module": "lab",
  "current_course_id": 4,
  "current_project": "local-minimum-rag",
  "current_lab_topic": "embedding",
  "current_review_id": null,
  "last_action": "experiment_completed",
  "recommended_next_action": "return_to_build",
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

### 字段说明

- `current_module`
  当前所在模块，建议枚举：
  - `home`
  - `learning`
  - `build`
  - `lab`
  - `review`
  - `profile`

- `current_course_id`
  当前相关课程编号。无课程上下文时可为空。

- `current_project`
  当前关联实战项目，如 `local-minimum-rag`。

- `current_lab_topic`
  当前实验主题，如 `embedding`、`rerank`。

- `current_review_id`
  当前评审上下文标识。V1 可为空或用时间戳 ID。

- `last_action`
  最近完成的关键动作。

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

### 实战进度

文件：

`progress/build-progress.json`

职责：

- 记录每个项目的当前阶段
- 记录已完成步骤
- 用于恢复最小 RAG 搭建现场

建议步骤枚举：

- `scenario`
- `chunking`
- `embedding`
- `vector_db`
- `retrieval`
- `rerank`
- `generation`
- `evaluation`

### 能力摘要

文件：

`progress/competency.json`

职责：

- 聚合学习、实战、实验、评审的长期结果
- 为推荐课程、实验和评审建议提供依据

建议能力维度：

- `rag_foundations`
- `embedding_selection`
- `vector_db_selection`
- `retrieval_design`
- `rerank_decision`
- `evaluation_design`
- `architecture_review`

建议等级枚举：

- `new`
- `developing`
- `good`
- `strong`

## 状态流转

### 首页进入学习中心

1. `current_module = home`
2. 用户选择学习
3. 更新：
   - `current_module = learning`
   - `current_course_id = <N>`
   - `last_action = lesson_started`

### 学习结束进入实战

课程讲解完成后更新：

- `current_module = learning`
- `last_action = lesson_completed`
- `recommended_next_action = start_build`

### 实战完成一个关键步骤

写入 `build-progress.json` 后更新：

- `current_module = build`
- `last_action = <step>_selected` 或 `<step>_completed`
- 根据阶段决定 `recommended_next_action`

### 从实战进入实验

当当前问题适合比较实验时：

- `current_module = lab`
- `current_lab_topic = <topic>`
- `last_action = experiment_started`

### 实验完成返回实战

- `current_module = lab`
- `last_action = experiment_completed`
- `recommended_next_action = return_to_build`

### 进入架构评审

- `current_module = review`
- `last_action = review_started`
- `recommended_next_action = complete_constraints`

### 评审完成

- `current_module = review`
- `last_action = review_completed`
- `recommended_next_action = review_profile` 或 `start_build`

## 推荐动作模型

推荐动作应固定在一小组可解释枚举中：

- `open_dashboard`
- `continue_learning`
- `start_build`
- `continue_build`
- `open_lab`
- `return_to_build`
- `start_review`
- `review_profile`

推荐本身不需要存大量说明，但应能由上层服务生成带理由的解释。
