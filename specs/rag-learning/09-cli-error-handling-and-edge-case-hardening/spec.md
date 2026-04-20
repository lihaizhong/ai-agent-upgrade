# Spec Change: CLI Error Handling And Edge Case Hardening

## Objective

把 `rag-learning` 的 CLI 从“原型级异常透传”升级为“产品级错误契约”，并补齐边界测试缺口，使终端用户和调用方都能拿到可解释、可处理的错误信息。

本次 change 主要解决：

1. 无效参数、未知项目/场景、文件损坏等异常直接抛出 traceback，破坏 JSON 输出契约
2. 当前测试集中在 happy path，缺少对空历史、无效输入、所有权冲突等边界的回归
3. `evals.json` 中的部分项目 ID 与 `platform-config.json` 不一致，可能导致 eval 失效

## Assumptions

1. CLI 输出保持 JSON-first，错误信息也必须能被 `json.loads` 消费
2. 异常分层：脚本内部抛 `ValueError` / `KeyError` / `FileNotFoundError`，CLI 层统一收敛为结构化错误
3. 不引入日志文件或外部监控，只改进 stdout/stderr 契约
4. 本次 change 不修改正常路径的业务逻辑

## Background

基准测试和代码审查发现以下问题：

- `build --start-project --project invalid-project` 直接输出 Python traceback，调用方无法安全解析
- `lab --record-result --topic invalid-topic` 同样抛出未包装异常
- `review --record-summary --scenario invalid-scenario` 行为一致
- 空 workspace 下 `profile --summary` 表现正确，但空历史文件下的 `lab --history` / `review --history` 缺少显式断言
- `evals.json` 引用 `customer-support-rag` 和 `中文 PDF 知识库原型` 作为实战项目，但 `platform-config.json` 的 `build_projects` 中无对应 ID

结果是：

- 终端用户看到堆栈而非可操作建议
- 下游自动化调用（如测试、CI、其他 skill）需要额外捕获非 JSON 输出
- eval 质量无法保证，因为项目 ID 漂移

## Scope

### 1. CLI 层统一异常包装

`__main__.py` 的 `main()` 需要：

- 捕获所有业务异常（`ValueError`、`KeyError`、文件 IO 异常）
- 返回统一 JSON 错误结构：
  ```json
  {
    "error": true,
    "error_type": "invalid_project",
    "message": "Unknown project ID: invalid-project",
    "module": "build"
  }
  ```
- 保持非零退出码
- 不吞掉真正需要排查的编程错误（如 `AttributeError` 仍可透传或单独标记）

### 2. 各模块输入校验强化

在 CLI 包装之前，先确保模块方法本身抛出清晰的异常信息：

- `BuildService.start_project()`: 项目 ID 不存在时抛 `ValueError("Unknown project ID: ...")`
- `LabService.blueprint()` / `record_result()`: topic 不存在时抛 `ValueError("Unknown lab topic: ...")`
- `ReviewService.template()` / `record_summary()`: scenario 不存在时抛 `ValueError("Unknown review scenario: ...")`
- `LearningService.lesson_meta()`: 课程 ID 超范围时抛 `ValueError("Course ID out of range: ...")`

### 3. 边界测试补充

新增 `tests/rag_learning/test_edge_cases.py`，覆盖：

- 无效项目 ID 的 `build` 调用返回结构化错误
- 无效 lab topic 的 `lab` 调用返回结构化错误
- 无效 review scenario 的 `review` 调用返回结构化错误
- 空历史文件下的 `lab --history` / `review --history` 返回空数组而非异常
- 损坏的 JSON 状态文件下 `profile --summary` 的行为（fallback 或错误）
- 显式测试 `evals.json` 中引用的项目/场景在配置中存在

### 4. evals.json 与 platform-config.json 一致性修复

- 检查 `evals.json` 中所有涉及 `build_projects` 和 `review_scenarios` 的引用
- 对齐 `platform-config.json`，删除或重命名已失效的引用
- 如项目 ID 确实不存在，在 eval 中改为使用现有项目 ID 或移除该 eval case

## Boundaries

- Always:
  - 错误输出必须是合法 JSON
  - 正常路径不得改变
  - 测试必须覆盖新增的错误分支
- Ask first:
  - 引入日志框架或遥测
  - 把错误信息国际化
  - 修改现有 eval 的判定逻辑（而不仅是 ID 对齐）
- Never:
  - 把 traceback 直接暴露给用户
  - 用 `except Exception:` 无差别吞掉所有异常
  - 修改正常路径的状态流转语义

## Success Criteria

- [x] CLI 无效输入返回结构化 JSON 错误而非 traceback
- [x] 新增边界测试覆盖所有模块的异常路径
- [x] `evals.json` 与 `platform-config.json` 项目/场景 ID 一致
- [x] 现有 24 个测试继续通过（实际 33 个，含新增 9 个边界测试）
- [x] `ruff check` 通过

## Non-Goals

- 不引入日志文件或外部监控
- 不修改正常路径的业务逻辑
- 不做性能优化（CLI 延迟已合格）
- 不重构模块内部异常体系

## Open Questions

1. 损坏的 JSON 状态文件应 fallback 到默认值，还是返回错误？
2. 是否需要在 SKILL.md 中补充“错误输出格式”的契约说明？
