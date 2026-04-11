# Plan: Workspace Fallback

## Status

- Status: Completed
- Created: 2026-04-11
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/09-workspace-fallback/spec.md)

## Objective

当 git user.name 未配置时不阻断流程，使用默认值继续：

- 允许无身份时继续使用 shared workspace
- 输出警告提示用户如何配置
- 默认值 workspace 不提交到仓库

## Implementation Strategy

按"先改核心逻辑，再补测试，最后补文档"的顺序。

原则：

1. 不阻断用户使用 skill
2. 通过警告引导用户配置正确身份
3. defaults workspace 在 gitignore 中

## Phase 1: Core Logic

Scope:

- 修改 `normalize_workspace_username()` 返回默认值而非抛异常
- 修改 `resolve_workspace_identity()` 检测空值并警告

Expected outcome:

- 无 git user.name 时返回 `defaults`，设置 `using_fallback: True`

## Phase 2: Integration

Scope:

- `ensure_workspace()` 返回值包含 `using_fallback`
- `.gitignore` 添加 defaults

Expected outcome:

- 返回值能告知调用方是否使用了回退

## Phase 3: Testing

Scope:

- 增加 `test_workspace_fallback.py`
- 覆盖空值场景

Expected outcome:

- 测试通过，无回归

## Verification Commands

```bash
uv run python -m pytest tests/prompt_learning/test_workspace_fallback.py -v
```

## Risks

1. 多用户共享 defaults workspace 可能造成数据混乱
2. 警告可能被用户忽略

通过 gitignore 和警告文案降低风险。