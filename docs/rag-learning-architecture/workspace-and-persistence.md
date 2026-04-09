# RAG Learning Workspace 与持久化设计

## 目标

为 `rag-learning` 提供统一、克制、可扩展的持久化机制，使平台能够保留必要的长期信息，同时避免把 workspace 变成杂乱的项目日志目录。

## Workspace 根目录

所有持久化信息统一放在项目根目录下：

`rag-learning-workspace/`

每个用户拥有独立空间：

`rag-learning-workspace/<username>/`

路径解析必须兼容 skill 软链接入口。无论脚本从 `agent-skills/rag-learning/`、`.opencode/skills/rag-learning/` 还是 `.codex/skills/rag-learning/` 启动，workspace 根目录都必须解析到项目根目录下的 `rag-learning-workspace/`，不能创建在 skill 目录、`.opencode/` 或 `.codex/` 下。

## 用户名规则

用户目录名生成规则如下：

1. 优先读取 `git config user.name`
2. 如果用户名中包含空格，将空格替换为 `-`
3. 如果读取失败或为空，使用 `default-zoom`

## 持久化原则

### 1. 只存长期有价值的信息

允许存储：

- 学习进度
- 当前项目与当前模块摘要
- 实验结果摘要
- 选型偏好
- 架构评审摘要

### 2. 不存中间过程

不保存：

- 中间推理
- 临时代码草稿
- 临时教学正文
- 未确认方案草稿
- 冗余对话日志

### 3. 优先存摘要，不存大段正文

例如实验记录保存变量、结果和结论摘要，而不是完整聊天过程。

## 推荐目录结构

```text
rag-learning-workspace/
  <username>/
    profile/
      learner.json
      preferences.json
    progress/
      current-state.json
      course-progress.json
      build-progress.json
      competency.json
    lab/
      experiment-history.jsonl
      insights.jsonl
    review/
      review-history.jsonl
      drafts/
```

## 目录职责

### `profile/`

保存用户元信息与稳定偏好。

#### `learner.json`

```json
{
  "workspace_user": "Li-Haizhong",
  "source_git_username": "Li Haizhong",
  "created_at": "2026-04-09T10:00:00+08:00",
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

#### `preferences.json`

```json
{
  "language": "zh-CN",
  "preferred_runtime": "python",
  "preferred_stack": "langchain",
  "deployment_preference": "hybrid",
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

### `progress/`

保存当前产品态、课程进度、实战进度和能力摘要。

#### `current-state.json`

记录当前平台上下文：

```json
{
  "current_module": "build",
  "current_course_id": 4,
  "current_project": "local-minimum-rag",
  "current_lab_topic": null,
  "last_action": "embedding_selected",
  "recommended_next_action": "choose_vector_db",
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

#### `course-progress.json`

记录课程完成情况：

```json
{
  "completed_courses": [1, 2],
  "in_progress_course": 4,
  "course_status": {
    "4": {
      "status": "in_progress",
      "started_at": "2026-04-09T09:30:00+08:00"
    }
  },
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

#### `build-progress.json`

记录项目推进情况：

```json
{
  "projects": {
    "local-minimum-rag": {
      "status": "in_progress",
      "current_step": "vector_db",
      "completed_steps": [
        "scenario",
        "chunking",
        "embedding"
      ],
      "last_updated_at": "2026-04-09T10:00:00+08:00"
    }
  },
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

#### `competency.json`

记录能力级摘要：

```json
{
  "areas": {
    "embedding_selection": {
      "level": "developing",
      "evidence_count": 2
    },
    "retrieval_evaluation": {
      "level": "new",
      "evidence_count": 0
    },
    "architecture_review": {
      "level": "good",
      "evidence_count": 1
    }
  },
  "updated_at": "2026-04-09T10:00:00+08:00"
}
```

### `lab/`

保存实验历史摘要和可复用洞察。

#### `experiment-history.jsonl`

每行记录一次实验摘要：

```json
{
  "timestamp": "2026-04-09T10:20:00+08:00",
  "topic": "embedding",
  "scenario": "local-minimum-rag",
  "variants": ["text-embedding-3-small", "bge-m3"],
  "metric_focus": ["hit_rate_at_5", "latency"],
  "summary": "中文数据下 bge-m3 召回更稳，但本地推理成本更高",
  "recommended_choice": "bge-m3"
}
```

#### `insights.jsonl`

每行保存一个已确认的长期结论：

```json
{
  "timestamp": "2026-04-09T10:25:00+08:00",
  "topic": "rerank",
  "insight": "在文档规模较小时先不引入 rerank，优先调 chunking 和 top-k",
  "source": "lab",
  "confidence": "medium"
}
```

### `review/`

保存方案评审摘要。

#### `review-history.jsonl`

每行记录一次方案摘要：

```json
{
  "timestamp": "2026-04-09T11:00:00+08:00",
  "scenario": "enterprise-knowledge-search",
  "constraints_summary": "中文为主，10 万级文档，要求私有部署",
  "recommended_stack": {
    "embedding": "bge-m3",
    "vector_db": "qdrant",
    "retrieval": "hybrid",
    "rerank": "bge-reranker-v2-m3"
  },
  "risk_summary": "评估数据集缺失，需先建立标注集"
}
```

### `review/drafts/`

只保存用户明确要求保留的草案快照，不默认写入每轮版本。

## V1 范围

V1 先做：

- `profile/`
- `progress/`
- `lab/experiment-history.jsonl`
- `review/review-history.jsonl`

`insights.jsonl` 与 `review/drafts/` 可作为后续增强。
