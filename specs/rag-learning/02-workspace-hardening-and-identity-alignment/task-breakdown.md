# Tasks: Workspace Hardening And Identity Alignment

## Status

- Status: Completed
- Updated: 2026-04-20
- Notes:
  - All spec-scoped tasks and verification gates are complete in the current codebase.
  - Follow-up workspace behavior changes should be tracked as a new spec change.

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/02-workspace-hardening-and-identity-alignment/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/02-workspace-hardening-and-identity-alignment/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Workspace Contract

- [x] Task: 引入统一的 workspace identity 解析结果
  - Acceptance: `workspace.py` 中存在单一入口返回 `explicit_username / source_git_username / workspace_user / using_fallback`
  - Verify: 审查 `workspace.py`
  - Files: `agent-skills/rag-learning/scripts/workspace.py`

- [x] Task: 为用户名规范化增加路径安全约束
  - Acceptance: 用户名净化后不能生成 `.`、`..`、路径分隔符或逃逸路径
  - Verify: 增加针对恶意用户名的单元测试
  - Files: `agent-skills/rag-learning/scripts/workspace.py`, `tests/rag_learning/`

- [x] Task: 增加 workspace ownership 与 metadata fail-fast 校验
  - Acceptance: `learner.json` 缺失或 `workspace_user` 不匹配时显式报错
  - Verify: 增加 mismatch 场景测试
  - Files: `agent-skills/rag-learning/scripts/workspace.py`, `tests/rag_learning/`

## Phase 2: Bootstrap Flow

- [x] Task: 修正 `workspace --bootstrap` 的首次创建行为
  - Acceptance: 新用户首次进入时创建 `rag-learning-workspace/<username>/`
  - Verify: CLI 测试检查目录和默认文件集
  - Files: `agent-skills/rag-learning/scripts/workspace.py`, `agent-skills/rag-learning/scripts/__main__.py`, `tests/rag_learning/test_platform.py`

- [x] Task: 对齐非 workspace 入口的 bootstrap 预处理
  - Acceptance: `home / learning / build / lab / review / profile` 在首次进入时使用同一套 bootstrap 规则
  - Verify: 搜索命令入口并执行最小集成测试
  - Files: `agent-skills/rag-learning/scripts/__main__.py`, `tests/rag_learning/`

## Phase 3: Module Alignment

- [x] Task: 对齐所有模块的 workspace 读取入口
  - Acceptance: 不存在旁路路径拼接或私有 workspace 解析逻辑
  - Verify: 代码搜索 + 最小模块验证
  - Files: `agent-skills/rag-learning/scripts/home.py`, `agent-skills/rag-learning/scripts/learning.py`, `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/review.py`, `agent-skills/rag-learning/scripts/profile.py`

## Phase 4: Testing

- [x] Task: 增加 workspace 首次创建测试
  - Acceptance: 新用户首次进入后，目录和默认文件集被创建
  - Verify: `python -m unittest tests.rag_learning.test_platform`
  - Files: `tests/rag_learning/test_platform.py`

- [x] Task: 增加路径安全测试
  - Acceptance: 恶意用户名输入不能逃逸 workspace 根目录
  - Verify: `python -m unittest tests.rag_learning.test_config_units`
  - Files: `tests/rag_learning/test_config_units.py`

- [x] Task: 增加 identity / ownership mismatch 测试
  - Acceptance: 命中错误 workspace 或 metadata 不一致时返回清晰错误
  - Verify: `python -m unittest tests.rag_learning.test_state_flow tests.rag_learning.test_platform`
  - Files: `tests/rag_learning/test_platform.py`, `tests/rag_learning/test_state_flow.py`

## Phase 5: Docs

- [x] Task: 更新 workspace 架构文档
  - Acceptance: 文档明确首次创建、用户隔离和 fallback 语义
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/workspace-and-persistence.md`

- [x] Task: 更新 `SKILL.md` 中的持久化与身份边界
  - Acceptance: `SKILL.md` 不再允许模糊命中已有 workspace
  - Verify: 文档审查
  - Files: `agent-skills/rag-learning/SKILL.md`

## Global Gates

- [x] Gate: workspace 仍然保持单层用户语义
  - Acceptance: 不新增 `actor`、`tenant` 等第二层目录
  - Verify: 路径实现审查

- [x] Gate: 错误通过显式检查暴露，而不是通过静默回退掩盖
  - Acceptance: 找不到目标 workspace 时只允许创建或报错，不允许复用已有目录
  - Verify: 代码审查 + 测试
