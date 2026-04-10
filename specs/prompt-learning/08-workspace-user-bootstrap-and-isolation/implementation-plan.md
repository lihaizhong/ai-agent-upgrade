# Plan: Workspace 用户解析与首次创建隔离

## Status

- Status: Completed
- Created: 2026-04-10
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/08-workspace-user-bootstrap-and-isolation/spec.md)

## Source of Truth

This plan is derived from:

- [08-workspace-user-bootstrap-and-isolation spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/08-workspace-user-bootstrap-and-isolation/spec.md)
- [01-learning-platform-rearchitecture spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/01-learning-platform-rearchitecture/spec.md)
- [workspace-and-persistence.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/docs/prompt-learning-architecture/workspace-and-persistence.md)
- [agent-skills/prompt-learning/scripts/workspace.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/prompt-learning/scripts/workspace.py)
- [agent-skills/prompt-learning/scripts/__main__.py](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/agent-skills/prompt-learning/scripts/__main__.py)

## Objective

让 `prompt-learning-workspace/<username>/` 真正成为用户级隔离边界：

- 当前用户必须稳定解析成唯一 workspace
- 新用户首次进入必须创建自己的 workspace
- 禁止回退到已有用户目录
- 所有模块共享同一套 workspace 解析与校验逻辑

## Implementation Strategy

按“先收敛规则，再统一入口，再补测试和文档”的顺序推进。

原则：

1. workspace 层负责用户隔离，不能把隔离责任下沉到 exam/practice 等模块
2. 不增加第二层 actor/worker 目录
3. 发现身份不一致时立即报错，不做隐式兼容

## Phase 1: Workspace Resolution Contract

Scope:

- 明确 `workspace_user` 的唯一解析规则
- 禁止扫描现有 workspace 目录后做回退选择
- 定义“目录不存在时创建、命中错误目录时报错”的行为

Expected outcome:

- `workspace.py` 成为唯一可信的 workspace 解析入口

## Phase 2: Bootstrap and Entry Enforcement

Scope:

- 校正 `workspace --bootstrap`
- 校正各产品入口首次进入时的 bootstrap 流程
- 保证解析结果与读写目录严格一致

Expected outcome:

- 新用户首次进入时自动创建自己的 workspace
- 任何入口都不会误入已有别人的 workspace

## Phase 3: Module Alignment

Scope:

- 检查 `home / learning / practice / exam / profile / lab`
- 确保全部模块只依赖统一 workspace 路径
- 清理任何可能的旁路路径解析或特殊兼容

Expected outcome:

- 所有状态文件都稳定落在 `prompt-learning-workspace/<workspace_user>/`

## Phase 4: Verification

Scope:

- 增加“新用户首次创建 workspace”的测试
- 增加“已有别人的 workspace 时不能回退复用”的测试
- 增加“显式 username 与实际命中目录不一致时报错”的测试

Expected outcome:

- 问题能稳定复现并被测试阻止回归

## Phase 5: Docs and Skill Guidance

Scope:

- 更新架构文档中的 workspace 规则
- 更新 skill contract 中关于持久化和用户目录的说明
- 去掉任何可能暗示“可复用现有 workspace”的文案

## Verification Commands

```bash
./.venv/bin/python -m unittest tests.prompt_learning.test_platform
./.venv/bin/python -m unittest tests.prompt_learning.test_state_flow
./.venv/bin/python -m unittest tests.prompt_learning.test_exam_session
```

```bash
./.venv/bin/ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```

## Risks

1. 上游调用链可能一直显式传入固定 `--username`
2. 现有样例 workspace 数据可能掩盖真实解析错误
3. 某些历史测试可能默认“目录已存在”

这些风险应通过暴露错误和补测试处理，而不是通过目录回退兼容。
