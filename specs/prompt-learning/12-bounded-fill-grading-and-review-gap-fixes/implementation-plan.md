# Plan: Bounded Fill Grading And Review Gap Fixes

## Status

- Status: Proposed
- Created: 2026-04-13
- Source: [spec.md](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/12-bounded-fill-grading-and-review-gap-fixes/spec.md)

## Source of Truth

This plan is derived from:

- [12-bounded-fill-grading-and-review-gap-fixes spec](/Users/lihaizhong/Documents/Project/ai-agent-upgrade/specs/prompt-learning/12-bounded-fill-grading-and-review-gap-fixes/spec.md)
- Existing prompt-learning scripts under `agent-skills/prompt-learning/scripts/`
- Existing regression suites in `tests/prompt_learning/`

## Overview

本次实现把剩余 review 问题拆成三个垂直切片：先用回归测试锁定当前缺陷，再把填空题判题改造成模式化分发，随后补齐 Prompt Lab 保存门禁和错题回练推荐语义，最后统一文档与全量验证。

## Dependency Graph

```text
Regression coverage
    │
    ├── Fill grading mode dispatch
    │       ├── term grading fix
    │       ├── range compatibility
    │       └── steps grading scaffold
    │
    ├── Prompt Lab save gate tightening
    │
    └── Practice recommendation alignment
             │
             └── Docs alignment and full verification
```

## Architecture Decisions

- 填空题改为“模式分发 + 小函数判题”架构，默认模式为 `term`；如答案本身呈现 range 特征，继续兼容现有区间语义。
- `acceptable_variants` 继续承担受约束语义等价表达的入口，不引入新的外部判题依赖。
- 模糊比较最多给部分分，不能再直接触发满分。
- Prompt Lab 的“审查通过”定义收紧为所有 checklist 项均为 `pass`。
- 练习推荐动作优先由持久化后的 `mistake_count` 决定，只要尚有未解决错题，就继续推荐 `review_mistakes`。

## Implementation Strategy

### Phase 1: Regression Coverage

Scope:

- 为三个 review 问题补最小失败前置测试
- 明确填空题“格式差异可通过、内容错误不可满分”的断言

Expected outcome:

- 新增测试在当前实现下能准确表达缺陷

### Phase 2: Fill Grading Refactor

Scope:

- 提供填空题模式解析与分发入口
- 新增 `term / range / steps` 判题小函数
- 让 `term` 模式的满分条件回到 exact / variant / normalized exact
- 让高相似度分支只触发部分分

Expected outcome:

- 中文术语 typo 不再满分
- 格式性差异与 range 兼容行为保持稳定

### Phase 3: Save Gate And Recommendation Alignment

Scope:

- 收紧 Prompt Lab 保存门禁
- 修正错题回练只完成部分修复时的推荐动作

Expected outcome:

- 模板保存语义与文档一致
- `current-state.json` 与 `mastery.json` 不再重新分叉

### Phase 4: Docs And Verification

Scope:

- 对齐考试、Prompt Lab、状态模型文档
- 跑 prompt-learning 全量测试和 lint

Expected outcome:

- 文档、实现、测试表达同一套规则

## Checkpoints

### Checkpoint: After Phases 1-2

- [ ] 填空题新增回归测试已通过
- [ ] whitespace-only / variants / range 行为仍然成立
- [ ] `tests/prompt_learning/test_exam_session.py` 通过

### Checkpoint: After Phase 3

- [ ] Prompt Lab 负向保存测试通过
- [ ] 部分解决错题时推荐动作测试通过
- [ ] `tests/prompt_learning/test_state_flow.py` 通过

### Checkpoint: Complete

- [ ] `tests.prompt_learning` 全绿
- [ ] `ruff check` 通过
- [ ] 文档与 spec 审查通过

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 新的判题模式接口破坏现有 fill 题 JSON | Medium | 保持所有新增字段可选，默认回落到 `term` |
| 取消高相似度满分后，部分现有测试 fixture 需要调整 | Medium | 先补精确断言，再按业务契约更新预期 |
| Prompt Lab 门禁收紧后，测试或文档仍默认“有 revisions 就能保存” | Medium | 同步修改负向测试和保存边界文档 |
| 推荐动作调整影响首页推荐断言 | Low | 直接在 `test_state_flow.py` 增加回归用例并保留显式动作优先级检查 |

## Parallelization Opportunities

- Safe to parallelize:
  - 文档更新可以在核心行为稳定后并行处理
  - 测试用例草稿与实现分析可以并行准备
- Must be sequential:
  - 填空题判题重构与其测试需要一起推进
  - Prompt Lab 保存门禁和推荐动作修复都依赖最终业务契约
- Needs coordination:
  - 如果多人同时修改 `test_exam_session.py`，先统一“满分 / 半分 / 错误”的新断言口径

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform tests.prompt_learning.test_exam_session tests.prompt_learning.test_state_flow tests.prompt_learning.test_workspace_fallback
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```
