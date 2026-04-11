# Spec: Prompt Learning Workspace Fallback

## Background

当 `git config user.name` 未配置时，prompt-learning skill 启动时会直接报错并退出，导致完全没有 workspace 可用。

## Problem

- 用户首次使用 skill 时，如果未配置 git user.name，无法进行任何学习活动
- 错误信息不够友好，没有提供解决方案

## Solution

当无法获取 git user.name 时：

1. 使用默认名 `defaults` 作为 workspace 目录名，继续后续流程
2. 输出警告信息，告知用户如何配置 git user.name
3. 将 `prompt-learning-workspace/defaults/` 加入 .gitignore，避免提交到仓库

## Changes

### workspace.py

- `DEFAULT_WORKSPACE_USERNAME = "defaults"`
- `normalize_workspace_username()`: 失败时返回默认值而非抛异常
- `resolve_workspace_identity()`: 检测到 git user.name 为空时，输出警告到 stderr 并返回 `using_fallback: True`
- `ensure_workspace()`: 返回值增加 `using_fallback` 字段

### .gitignore

添加 `prompt-learning-workspace/defaults/`

## Backward Compatibility

已有配置 git user.name 的用户不受影响，使用默认值时会触发警告，但不是阻断错误。