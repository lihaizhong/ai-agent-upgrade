# Plan: Workspace Hardening And State Alignment

## Status

- Status: Proposed
- Created: 2026-04-12
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/10-workspace-hardening-and-state-alignment/spec.md)

## Source of Truth

This plan is derived from:

- [10-workspace-hardening-and-state-alignment spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/10-workspace-hardening-and-state-alignment/spec.md)
- [09-workspace-fallback spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/09-workspace-fallback/spec.md)
- [workspace-and-persistence.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/workspace-and-persistence.md)
- [state-model.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/state-model.md)
- [prompt-lab.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/prompt-lab.md)

## Objective

在不改变平台核心模块结构的前提下，完成一次“行为契约统一 + 安全收口 + 状态闭环修复”的改动：

- fallback 行为统一
- 路径安全收口
- 首页推荐与状态模型对齐
- 错题回练与 mastery 口径对齐
- Prompt Lab 保存门槛与文档对齐

## Implementation Strategy

按“先收敛契约，再做高风险安全修复，再修状态流，再收紧保存边界，最后回归”的顺序推进。

### Phase 1: Contract Alignment

Scope:

- 统一 fallback 行为的文档与测试
- 去掉仍要求 fail-closed 的冲突表述

Expected outcome:

- `defaults fallback` 成为唯一身份策略

### Phase 2: Path Safety

Scope:

- 安全化 `workspace_user`
- 安全化报告文件名
- 为异常输入补测试

Expected outcome:

- 所有落盘路径都只使用安全后的标识

### Phase 3: State And Recommendation Alignment

Scope:

- 让首页推荐优先消费显式 `recommended_next_action`
- 让错题 resolved 回流 mastery

Expected outcome:

- 首页推荐与状态模型一致
- 错题本和 mastery 不再相互打架

### Phase 4: Prompt Lab Save Gate

Scope:

- 保存模板前要求槽位完整
- 保存模板前要求草稿校验通过
- 保存模板前要求用户显式确认

Expected outcome:

- 只有合格模板能进入 workspace

### Phase 5: Verification

Scope:

- 全量 prompt-learning 测试回归
- lint 回归
- 检查示例 workspace 输出是否与文档一致

## Risks

1. 现有测试 fixture 可能依赖旧的宽松保存/推荐行为
2. 用户名安全化会改变历史路径或报告命名格式
3. mastery 修正规则如果写得太复杂，会降低可解释性

## Mitigations

1. 先写测试表达新契约，再最小改实现
2. 展示名与路径名分离，减少对用户可见行为的影响
3. mastery 先采用简单抵扣模型，避免一次引入复杂分数系统

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_workspace_fallback
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```
