# Tasks: Config Source Unification And Module Handoff

## Status

- Status: Completed
- Updated: 2026-04-20
- Notes:
  - All spec-scoped tasks and verification gates are complete in the current codebase.
  - Future configuration-surface expansion should be tracked as a new spec change rather than appended here.

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/05-config-source-unification-and-module-handoff/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/05-config-source-unification-and-module-handoff/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Config Boundary Definition

- [x] Task: 明确 `catalog`、`platform-config`、`courses` 的职责边界
  - Acceptance: 文档和代码层都能回答“某类元数据应该放在哪里”
  - Verify: 配置边界审查
  - Files: `docs/rag-learning-architecture/cli-and-modules.md`, `agent-skills/rag-learning/reference/`

- [x] Task: 定义 build 配置目标结构
  - Acceptance: project metadata、step sequence、competency mapping、next-step 信息都有结构化 schema
  - Verify: 配置 schema 审查
  - Files: `agent-skills/rag-learning/reference/platform-config.json`, `agent-skills/rag-learning/scripts/config.py`

- [x] Task: 定义模块 handoff 字段集合
  - Acceptance: learning/build/lab/review/profile 之间的关键 handoff 字段有明确列表
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/build-center.md`, `docs/rag-learning-architecture/rag-lab.md`, `docs/rag-learning-architecture/architecture-review.md`

## Phase 2: Build Config Extraction

- [x] Task: 将 build project metadata 从硬编码迁移到配置源
  - Acceptance: `PROJECT_OVERRIDES` 不再承担主配置职责
  - Verify: `build --entry-points` 输出检查
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/config.py`, `agent-skills/rag-learning/reference/platform-config.json`

- [x] Task: 将 build step panel 配置从硬编码迁移到配置源
  - Acceptance: `STEP_PANELS` 不再承担主配置职责
  - Verify: `build --step-panel` 输出检查
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/reference/platform-config.json`

## Phase 3: Handoff And Validation

- [x] Task: 为 build -> lab 增加显式 handoff 字段
  - Acceptance: 进入 lab 时可拿到 project / step / recommended topic 等 summary 信息
  - Verify: 状态流测试
  - Files: `agent-skills/rag-learning/scripts/build.py`, `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/state.py`

- [x] Task: 为 build/lab -> review 增加显式 evidence handoff
  - Acceptance: review 可以消费结构化 evidence summary，而不是只依赖隐式当前状态
  - Verify: 状态流测试
  - Files: `agent-skills/rag-learning/scripts/lab.py`, `agent-skills/rag-learning/scripts/review.py`, `agent-skills/rag-learning/scripts/state.py`

- [x] Task: 增加配置加载期校验
  - Acceptance: 配置缺失、非法枚举、断裂 step graph 会尽早报错
  - Verify: `python -m unittest tests.rag_learning.test_config_units`
  - Files: `agent-skills/rag-learning/scripts/config.py`, `agent-skills/rag-learning/scripts/build.py`, `tests/rag_learning/test_config_units.py`

## Phase 4: Docs And Verification

- [x] Task: 更新 build/lab/review 架构文档
  - Acceptance: 文档反映统一配置源和 handoff 设计
  - Verify: 文档审查
  - Files: `docs/rag-learning-architecture/build-center.md`, `docs/rag-learning-architecture/rag-lab.md`, `docs/rag-learning-architecture/architecture-review.md`, `docs/rag-learning-architecture/cli-and-modules.md`

- [x] Task: 增加配置与 handoff 回归测试
  - Acceptance: 平台测试和状态流测试覆盖关键 handoff 与配置一致性
  - Verify: `python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow`
  - Files: `tests/rag_learning/test_platform.py`, `tests/rag_learning/test_state_flow.py`

- [x] Task: 完成 lint 与全量验证
  - Acceptance: `ruff check` 和相关测试通过
  - Verify: `ruff check` + 单元测试
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [x] Gate: 不再由脚本硬编码大型平台配置面板
  - Acceptance: build 的主要结构化定义来自配置源
  - Verify: 代码审查

- [x] Gate: handoff 使用显式结构化字段，而不是隐式状态猜测
  - Acceptance: build -> lab -> review 的核心输入可追踪
  - Verify: 代码审查 + 状态流测试
