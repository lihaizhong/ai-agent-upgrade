# Plan: Profile Preference Rollup And Progress Semantics

## Status

- Status: Implemented
- Created: 2026-04-20
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/08-profile-preference-rollup-and-progress-semantics/spec.md)

## Source of Truth

This plan is derived from:

- [08-profile-preference-rollup-and-progress-semantics spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/08-profile-preference-rollup-and-progress-semantics/spec.md)
- [profile.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/profile.md)
- [workspace-and-persistence.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/workspace-and-persistence.md)
- Existing `profile.py`, `lab.py`, and `review.py` implementations

## Objective

把 learning profile 从“历史回看”扩成“真实进度 + 稳定偏好”的长期沉淀模块：

- `preferences.json` 不再只是目录占位
- `profile --summary` 能表达稳定判断
- 项目活跃/完成统计不再含糊

## Implementation Strategy

按“先定义偏好 schema，再补聚合来源，再扩 summary 输出，最后收口持久化与文档”的顺序推进。

依赖顺序：

1. 先明确偏好来源和聚合规则
2. 再调整 `profile.py` 与相关写入路径
3. 最后对齐 workspace/profile 文档和测试

## Phase 1: Preference Schema And Regression Coverage

Scope:

- 定义 `preferences.json` 的目标结构
- 补 profile progress 和偏好回归测试
- 锁定 active/completed count 期望

Expected outcome:

- 偏好和进度语义先被测试表达

## Phase 2: Preference Rollup Implementation

Scope:

- 从实验与评审结构化结果中聚合稳定偏好
- 明确冲突偏好的聚合顺序
- 让 `preferences.json` 成为单一真相

Expected outcome:

- 平台开始形成稳定的用户级判断沉淀

## Phase 3: Profile Summary Alignment

Scope:

- 扩展 `profile --summary`
- 修正 active/completed project 统计
- 暴露偏好证据摘要

Expected outcome:

- 用户可以从档案中看到“我已经形成了哪些选择倾向”

## Phase 4: Docs And Verification

Scope:

- 更新 profile / workspace / overview docs
- 跑平台、状态流和内容测试

Expected outcome:

- 偏好沉淀语义在文档和实现中一致

## Checkpoints

### Checkpoint: After Phases 1-2

- [x] `preferences.json` 结构已明确
- [x] 偏好来源不再依赖自由生成
- [x] 冲突偏好有稳定聚合规则（最近证据优先）

### Checkpoint: Complete

- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_state_flow` 通过
- [x] `tests.rag_learning.test_content_quality` 通过
- [x] `ruff check` 通过
- [x] profile / workspace / overview 文档审查通过

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 单次实验结果被误判为稳定偏好 | Medium | 聚合时保留来源与证据计数，不直接绝对化 |
| `preferences.json` 与 `profile --summary` 各自演化成双真相 | Medium | 明确其中一层为单一真相，另一层只做消费 |
| 进度统计修复和偏好聚合改动耦合过深 | Low | 先定义 schema，再分别落地计数与偏好逻辑 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_content_quality
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
