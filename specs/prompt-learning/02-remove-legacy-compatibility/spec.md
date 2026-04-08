# Spec: Prompt Learning 移除 Legacy 兼容层

## Assumptions

以下假设基于 `01-learning-platform-rearchitecture` 已完成实现这一前提整理。

1. `prompt-learning` 的平台化重构已经完成，新的模块边界已经存在：
   - `workspace`
   - `home`
   - `learning`
   - `practice`
   - `exam`
   - `lab`
   - `profile`
2. 用户已经明确决定，新版本不需要继续兼容旧的模式心智和旧 CLI 接口。
3. 旧接口主要包括：
   - `mode`
   - `learn`
   - `generate`
   - `state`
   - 以及为兼容这些旧接口保留的 `engine.py`
4. 本次工作目标不是新增产品能力，而是去掉旧兼容层，让 `prompt-learning` 彻底成为新产品。
5. 删除兼容层后，`SKILL.md`、脚本、参考文档和规格文档应保持一致，不再混用“旧模式”和“新平台”两套心智。
6. 这次调整可能影响现有 eval、reference 文档和 agent 配置，因此需要把“文档与配置清理”纳入范围。

## Objective

将 `prompt-learning` 从“新平台 + 旧接口兼容层”进一步收敛为“只保留新平台接口的全新产品”。

本次工作要解决的问题：

- 旧 `learn / generate / state / mode` 入口仍然存在，容易让未来维护者误以为两套心智都有效
- `engine.py` 虽然已缩成兼容包装层，但它仍然暗示旧架构还被正式支持
- 旧 reference 文档、旧描述和新平台 contract 共存，会继续造成边界模糊
- 后续如果继续增强产品能力，兼容层会成为额外负担

本次工作完成后，应满足：

- CLI 只保留新平台入口
- `engine.py` 不再承担任何对外兼容职责，必要时删除
- `SKILL.md` 只描述新平台心智
- 文档和配置不再提示或依赖旧模式接口
- 后续所有增强工作默认基于新平台接口展开

## Non-Goals

本 spec 不包括以下内容：

- 新增新的学习、练习、考试或 Prompt Lab 功能
- 重做状态模型或 workspace 结构
- 建立完整自动化测试体系
- 重写所有历史文档，仅清理与当前产品边界直接冲突的内容

## Scope

本次工作应覆盖：

1. CLI 收敛
- 删除旧 `mode`
- 删除旧 `learn`
- 删除旧 `generate`
- 删除旧 `state`
- 只保留 `workspace / home / learning / practice / exam / lab / profile`

2. 兼容实现清理
- 删除 `engine.py`，或至少使其不再被导出和不再作为正式接口存在
- 删除仅为旧兼容层保留的转调逻辑

3. Skill contract 收敛
- 确认 `SKILL.md` 不再出现旧模式心智
- 如有必要，补充“仅支持平台模块”的明确表述

4. 文档与参考资料清理
- 清理仍然以 `learn / exam / generate` 作为主叙事的 reference 文档
- 更新可能引用旧接口的 docs/specs/evals/config
- 明确 `01-learning-platform-rearchitecture` 已完成，`02` 负责移除 legacy

5. 配置与导出清理
- 清理 `__init__.py` 中不再需要的 legacy exports
- 检查 `agents/openai.yaml`、`evals/evals.json`、`VERSION.md` 等是否仍引用旧接口

## Success Criteria

以下条件全部满足时，本 spec 才算完成：

1. 在 `scripts/__main__.py` 中，用户可见的命令面只剩新平台模块。
2. `scripts/engine.py` 不再作为正式接口存在；若保留文件，也必须明确标记为内部遗留且不被导出、不被文档引用。
3. `scripts/__init__.py` 不再导出 `PromptLearningEngine`。
4. `SKILL.md`、reference、specs、配置文件中，不再把旧模式作为有效使用方式。
5. 至少完成一次 lint 和一次新平台主命令面验证。

## Commands

### Lint

```bash
ruff check .opencode/skills/prompt-learning/scripts
```

### New Platform CLI Verification

```bash
.venv/bin/python -m scripts home --dashboard
.venv/bin/python -m scripts learning --catalog
.venv/bin/python -m scripts practice --entry-points
.venv/bin/python -m scripts exam --entry-points
.venv/bin/python -m scripts lab --workflow --topic "会议纪要总结"
.venv/bin/python -m scripts profile --summary
```

### Cleanup Inspection

```bash
rg "PromptLearningEngine|learn --|generate --|mode|state --" .opencode/skills/prompt-learning
git diff -- .opencode/skills/prompt-learning specs/prompt-learning
```

## Project Structure

本次工作主要涉及：

```text
.opencode/skills/prompt-learning/
  SKILL.md
  scripts/
    __main__.py
    __init__.py
    engine.py
  reference/
  evals/
  agents/
  VERSION.md

specs/prompt-learning/
  01-learning-platform-rearchitecture/
  02-remove-legacy-compatibility/
```

## Risks

1. 直接删除旧入口后，可能有少量本地使用方式失效。
2. reference/evals/config 中若仍隐含旧模式假设，删除接口后会产生文档失真。
3. 如果只删命令不删文档，用户仍会被旧心智误导。

## Open Questions

1. `engine.py` 是直接删除，还是保留为空壳并标记 deprecated？
2. `reference/learning-mode.md`、`reference/exam-mode.md`、`reference/prompt-generation-mode.md` 是删除、归档，还是改写为新平台说明？
3. `mode` 命令是否直接移除，还是短期保留为“返回平台首页提示”的软过渡？
