# Tasks: Workspace Fallback

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/09-workspace-fallback/spec.md)

Tasks are ordered by dependency.

## Phase 1: Core Logic

- [x] Task: 添加默认用户名常量 `DEFAULT_WORKSPACE_USERNAME = "defaults"`
  - Acceptance: workspace 解析失败时不抛异常，而是返回默认值
  - Verify: 审查 `workspace.py`
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`

- [x] Task: 修改 `normalize_workspace_username()` 返回默认值而非抛异常
  - Acceptance: 输入为空时返回 "defaults"
  - Verify: 单元测试
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`

- [x] Task: 修改 `resolve_workspace_identity()` 检测空值并输出警告
  - Acceptance: git user.name 为空时打印警告并设置 `using_fallback: True`
  - Verify: 调用并观察 stderr
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`

## Phase 2: Integration

- [x] Task: `ensure_workspace()` 返回值包含 `using_fallback`
  - Acceptance: 返回 dict 含 `using_fallback: True/False`
  - Verify: 集成测试
  - Files: `agent-skills/prompt-learning/scripts/workspace.py`

- [x] Task: 添加 defaults workspace 到 .gitignore
  - Acceptance: 不提交到仓库
  - Verify: git status 检查
  - Files: `.gitignore`

## Phase 3: Testing

- [x] Task: 添加回退逻辑单元测试
  - Acceptance: 覆盖空值场景
  - Verify: `pytest tests/prompt_learning/test_workspace_fallback.py`
  - Files: `tests/prompt_learning/test_workspace_fallback.py`

- [x] Task: 添加回退 workspace 创建测试
  - Acceptance: defaults workspace 及文件集正确创建
  - Verify: 集成测试
  - Files: `tests/prompt_learning/test_workspace_fallback.py`

## Global Gates

- [x] Gate: 无 git user.name 时不阻断流程
  - Acceptance: skill 继续执行，只是使用共享 workspace
  - Verify: 运行测试

- [x] Gate: 警告信息输出到 stderr
  - Acceptance: 用户能看到如何解决问题
  - Verify: 检查输出