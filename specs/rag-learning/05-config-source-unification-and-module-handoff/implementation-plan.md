# Plan: Config Source Unification And Module Handoff

## Status

- Status: Implemented
- Updated: 2026-04-20
- Execution record: see [task-breakdown.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/05-config-source-unification-and-module-handoff/task-breakdown.md)
- Notes:
  - The scoped config-source unification and module handoff work has been implemented in the current codebase.
  - Build configuration now comes from the shared config source, handoff fields are explicit, and validation/docs/test coverage are aligned.

## Source of Truth

This plan is derived from:

- [05-config-source-unification-and-module-handoff spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/05-config-source-unification-and-module-handoff/spec.md)
- [01-learning-platform-rearchitecture spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/01-learning-platform-rearchitecture/spec.md)
- Existing config/build/lab/review implementations in `agent-skills/rag-learning/scripts/`

## Objective

把 `rag-learning` 的平台配置收敛为可解释、可校验、可 handoff 的结构：

- build 不再依赖大型硬编码常量
- `catalog`、`platform-config`、`courses` 各自职责清楚
- build -> lab -> review 的 handoff 由显式字段表达
- 配置缺口可以通过测试与加载期校验尽早暴露

## Implementation Strategy

按“先明确配置职责，再抽离 build 配置，再补 handoff 与校验”的顺序推进。

依赖顺序：

1. 先定义配置边界和配置 schema
2. 再迁移 build 常量到结构化配置
3. 再实现 handoff 字段和配置校验
4. 最后更新文档与测试

## Architecture Decisions

- `catalog.md` 继续承担学习目录和课程主线信息
- `platform-config.json` 或等价结构承担 build / lab / review 运行时配置
- `courses/` 只承载教学正文，不再作为运行期结构配置源
- handoff 只保存 summary 级结构化信息，不保存过程日志

## Phase 1: Config Boundary Definition

Scope:

- 明确 `catalog`、`platform-config`、`courses` 的职责
- 定义 build 配置的目标结构
- 定义 handoff 字段集合

Expected outcome:

- 后续迁移有稳定配置边界，不会继续引入双真相

## Phase 2: Build Config Extraction

Scope:

- 将 `PROJECT_OVERRIDES` 与 `STEP_PANELS` 抽离为结构化配置
- 保持 CLI 输出字段稳定

Expected outcome:

- `build.py` 从硬编码编排转为配置驱动编排

## Phase 3: Handoff And Validation

Scope:

- 为 build -> lab -> review 增加显式 handoff 字段
- 增加配置加载期校验
- 增加无效枚举和断裂 step graph 的测试

Expected outcome:

- 配置错误和 handoff 缺口能在测试中暴露

## Phase 4: Docs And Verification

Scope:

- 更新模块文档和配置说明
- 跑配置、平台和状态流测试

Expected outcome:

- docs、config、code、tests 对同一模块结构表达一致

## Checkpoints

### Checkpoint: After Phases 1-2

- [x] build 项目与 step 配置已脱离大型硬编码结构
- [x] `catalog` 与 `platform-config` 职责边界清楚
- [x] CLI 输出字段未回归

### Checkpoint: Complete

- [x] `tests.rag_learning.test_config_units` 通过
- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_state_flow` 通过
- [x] `ruff check` 通过
- [x] build/lab/review 文档审查通过

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 一次性迁移太多配置，导致 CLI 输出漂移 | Medium | 先固定输出 contract，再只替换内部数据来源 |
| handoff 设计过重，反而把状态模型复杂化 | Medium | 只保留 summary 级字段，不引入流程日志 |
| `catalog` 与 `platform-config` 职责仍然重叠 | Medium | 先在文档中定义清楚边界，再开始代码迁移 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_config_units
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
