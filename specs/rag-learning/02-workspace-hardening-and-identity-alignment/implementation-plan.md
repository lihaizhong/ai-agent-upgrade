# Plan: Workspace Hardening And Identity Alignment

## Status

- Status: Implemented
- Updated: 2026-04-20
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/02-workspace-hardening-and-identity-alignment/task-breakdown.md)
- Notes:
  - The scoped workspace hardening and identity alignment work has been implemented in the current codebase.
  - `workspace.py`, CLI bootstrap enforcement, regression coverage, and workspace contract docs are aligned.

## Source of Truth

This plan is derived from:

- [02-workspace-hardening-and-identity-alignment spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/02-workspace-hardening-and-identity-alignment/spec.md)
- [01-learning-platform-rearchitecture spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/spec.md)
- [workspace-and-persistence.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/rag-learning-architecture/workspace-and-persistence.md)
- [agent-skills/rag-learning/scripts/workspace.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/rag-learning/scripts/workspace.py)

## Objective

让 `rag-learning-workspace/<username>/` 真正成为用户级隔离边界：

- 当前用户稳定解析成唯一 workspace
- 新用户首次进入时创建自己的 workspace
- identity mismatch 和 ownership mismatch 显式报错
- 所有模块共享同一套 workspace 解析与校验逻辑

## Implementation Strategy

按“先收敛 identity contract，再统一入口，再补测试与文档”的顺序推进。

原则：

1. workspace 层负责路径安全和 ownership 校验，其他模块不旁路实现
2. 只保留单层用户 workspace，不引入第二层隔离目录
3. 对 fallback 语义只允许保留一种真相，不能让 code / docs / tests 分裂

## Dependency Graph

```text
Workspace identity contract
    │
    ├── Bootstrap and entry enforcement
    │
    ├── Module alignment
    │
    └── Tests and docs alignment
```

## Phase 1: Workspace Identity Contract

Scope:

- 明确 workspace identity 解析结果
- 增加用户名净化与路径逃逸保护
- 增加 ownership / metadata fail-fast 校验

Expected outcome:

- `workspace.py` 成为唯一可信的 workspace 解析入口

## Phase 2: Bootstrap And Entry Enforcement

Scope:

- 修正 `workspace --bootstrap`
- 统一非 workspace 命令的预启动 bootstrap 行为
- 保证解析结果与真实读写目录严格一致

Expected outcome:

- 新用户首次进入时创建自己的 workspace
- 任何入口都不会静默复用已有其他用户目录

## Phase 3: Module Alignment

Scope:

- 对齐 `home / learning / build / lab / review / profile`
- 确保全部模块只依赖统一 workspace 路径
- 清理任何隐式路径拼接或旁路逻辑

Expected outcome:

- 所有状态文件稳定落在 `rag-learning-workspace/<workspace_user>/`

## Phase 4: Verification

Scope:

- 增加 workspace 首次创建测试
- 增加路径安全测试
- 增加 ownership mismatch 与 identity mismatch 测试

Expected outcome:

- workspace 边界能通过自动化测试稳定回归

## Phase 5: Docs And Contract

Scope:

- 更新 workspace 架构文档
- 更新 `SKILL.md` 中的持久化与身份边界说明
- 对齐 fallback 语义和首次进入规则

Expected outcome:

- spec、实现、测试和文档共享同一套 workspace 语义

## Checkpoints

### Checkpoint: After Phases 1-2

- [x] identity 解析入口唯一
- [x] 恶意用户名无法逃逸 workspace 根目录
- [x] bootstrap 只创建当前用户目录

### Checkpoint: Complete

- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_state_flow` 通过
- [x] `tests.rag_learning.test_config_units` 通过
- [x] `ruff check` 通过
- [x] workspace 文档与 `SKILL.md` 审查通过

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 当前调用链默认依赖宽松 `--username` 逻辑 | Medium | 先把 identity contract 写清，再通过测试暴露上游不一致 |
| fallback 语义讨论拉长，阻塞实现 | Medium | 先把 open question 留在 spec，落地时只允许保留一种行为 |
| 某些测试目录或样例目录掩盖 ownership 问题 | Low | 用独立测试用户名和临时 workspace 场景覆盖 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_config_units
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
