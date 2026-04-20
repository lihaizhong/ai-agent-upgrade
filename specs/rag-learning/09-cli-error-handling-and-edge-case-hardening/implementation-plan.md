# Plan: CLI Error Handling And Edge Case Hardening

## Status

- Status: Implemented
- Created: 2026-04-20
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/09-cli-error-handling-and-edge-case-hardening/spec.md)

## Source of Truth

This plan is derived from:

- [09-cli-error-handling-and-edge-case-hardening spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/rag-learning/09-cli-error-handling-and-edge-case-hardening/spec.md)
- [Benchmark report](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/tests/rag_learning/benchmark.py)
- Existing `__main__.py`, `build.py`, `lab.py`, `review.py`, `learning.py` implementations

## Objective

把 CLI 异常从 traceback 升级为结构化 JSON 错误，并补齐边界测试与 eval 一致性。

## Implementation Strategy

按“先定义错误契约，再补模块校验，再扩 CLI 包装，最后对齐 eval 与测试”的顺序推进。

依赖顺序：

1. 定义统一错误 JSON schema
2. 强化模块输入校验信息
3. CLI 层统一异常包装
4. 补充边界测试与 eval 对齐

## Phase 1: Error Contract Definition

Scope:

- 确定统一 JSON 错误结构
- 确定错误类型枚举（invalid_project, unknown_topic, unknown_scenario, invalid_course, io_error 等）
- 确定退出码策略

Expected outcome:

- 错误 schema 被文档和测试共同引用

## Phase 2: Module Input Validation Hardening

Scope:

- `BuildService.start_project()`: 项目 ID 校验
- `LabService.blueprint()` / `record_result()`: topic 校验
- `ReviewService.template()` / `record_summary()`: scenario 校验
- `LearningService.lesson_meta()`: 课程 ID 范围校验

Expected outcome:

- 所有模块在异常时都抛出带清晰信息的 `ValueError`

## Phase 3: CLI Error Wrapper

Scope:

- `__main__.py` `main()` 增加 try/except 包装
- 将已知异常映射为结构化 JSON 错误
- 保持非零退出码

Expected outcome:

- CLI 始终输出合法 JSON（成功或错误）

## Phase 4: Edge Case Tests And Eval Alignment

Scope:

- 新增 `tests/rag_learning/test_edge_cases.py`
- 对齐 `evals.json` 与 `platform-config.json`
- 跑全量测试与 lint

Expected outcome:

- 边界测试覆盖所有新增错误分支
- eval 引用与配置一致

## Checkpoints

### Checkpoint: After Phase 3

- [x] CLI 无效输入返回结构化错误
- [x] 现有测试不受影响

### Checkpoint: Complete

- [x] `tests.rag_learning.test_platform` 通过
- [x] `tests.rag_learning.test_state_flow` 通过
- [x] `tests.rag_learning.test_content_quality` 通过
- [x] `tests.rag_learning.test_edge_cases` 通过
- [x] `ruff check` 通过
- [x] `evals.json` 与 `platform-config.json` ID 一致

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| CLI 包装层过宽，吞掉真正的编程错误 | High | 只捕获 `ValueError`、`KeyError`、IOError；`AttributeError`、`TypeError` 继续透传 |
| 新增边界测试与现有测试共享 workspace 导致污染 | Medium | 使用独立 test username 和 setUp/tearDown |
| eval 修改导致评测逻辑变化 | Low | 只改 ID 引用，不改判定逻辑 |

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform tests.rag_learning.test_state_flow tests.rag_learning.test_content_quality tests.rag_learning.test_edge_cases
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```
