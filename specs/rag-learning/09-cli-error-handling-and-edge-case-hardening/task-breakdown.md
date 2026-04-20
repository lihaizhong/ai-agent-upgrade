# Tasks: CLI Error Handling And Edge Case Hardening

## Source of Truth

This task breakdown is derived from:

- [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/09-cli-error-handling-and-edge-case-hardening/spec.md)
- [implementation-plan.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/09-cli-error-handling-and-edge-case-hardening/implementation-plan.md)

Tasks are ordered by dependency.

## Phase 1: Error Contract Definition

- [x] Task: 定义统一 JSON 错误 schema
  - Acceptance: 错误结构包含 `error`, `error_type`, `message`, `module` 字段
  - Verify: 文档审查 + 代码审查
  - Files: `agent-skills/rag-learning/scripts/__main__.py` (新增错误包装逻辑)

## Phase 2: Module Input Validation Hardening

- [x] Task: 强化 build 模块项目 ID 校验
  - Acceptance: `start_project("invalid")` 抛出清晰 `ValueError`
  - Verify: 边界测试
  - Files: `agent-skills/rag-learning/scripts/build.py`

- [x] Task: 强化 lab 模块 topic 校验
  - Acceptance: `blueprint("invalid")` / `record_result(topic="invalid")` 抛出清晰 `ValueError`
  - Verify: 边界测试
  - Files: `agent-skills/rag-learning/scripts/lab.py`

- [x] Task: 强化 review 模块 scenario 校验
  - Acceptance: `template("invalid")` / `record_summary(scenario="invalid")` 抛出清晰 `ValueError`
  - Verify: 边界测试
  - Files: `agent-skills/rag-learning/scripts/review.py`

- [x] Task: 强化 learning 模块课程 ID 校验
  - Acceptance: `lesson_meta(999)` 抛出清晰 `ValueError`
  - Verify: 边界测试
  - Files: `agent-skills/rag-learning/scripts/learning.py`

## Phase 3: CLI Error Wrapper

- [x] Task: 在 `__main__.py` 增加统一异常包装
  - Acceptance: CLI 始终输出合法 JSON；已知异常映射为结构化错误；非零退出码
  - Verify: 边界测试 + CLI 手动检查
  - Files: `agent-skills/rag-learning/scripts/__main__.py`

## Phase 4: Edge Case Tests And Eval Alignment

- [x] Task: 新增边界测试 `test_edge_cases.py`
  - Acceptance: 覆盖无效项目/ topic / scenario / 课程 ID、空历史、损坏 JSON 等边界
  - Verify: `python -m unittest tests.rag_learning.test_edge_cases`
  - Files: `tests/rag_learning/test_edge_cases.py`

- [x] Task: 对齐 `evals.json` 与 `platform-config.json`
  - Acceptance: eval 中引用的所有项目 ID 和 scenario ID 在配置中存在
  - Verify: 内容测试 + 人工审查
  - Files: `agent-skills/rag-learning/evals/evals.json`, `agent-skills/rag-learning/reference/platform-config.json`

- [x] Task: 全量测试与 lint 验证
  - Acceptance: 所有测试和 Ruff 全部通过
  - Verify: `python -m unittest tests.rag_learning` + `ruff check`
  - Files: `agent-skills/rag-learning/scripts/`, `tests/rag_learning/`

## Global Gates

- [x] Gate: CLI 不再暴露 traceback
  - Acceptance: 任何无效输入都返回结构化 JSON 错误
  - Verify: 边界测试 + CLI 输出检查

- [x] Gate: eval 引用与配置一致
  - Acceptance: `evals.json` 中所有项目/场景 ID 可在 `platform-config.json` 中找到
  - Verify: 内容测试 + 人工审查
