# Spec: RAG Learning 平台化重构

## Assumptions

以下假设基于当前仓库结构、已有讨论结果和现有 `rag-learning` skill 状态整理。在进入计划和实施前，默认这些假设成立；如果不成立，应先修订本 spec。

1. 本次工作是对现有 `agent-skills/rag-learning/` 做重构，不是创建一个全新 skill。
2. `rag-learning` 未来定位为一个平台型 skill，而不是保留现有“学习 / 实战 / 专题问答”三路径心智。
3. `SKILL.md` 将被收缩为 agent contract，不再承载流程细节、状态 schema 和模块设计。
4. 用户级持久化数据应统一落在项目根目录下的 `rag-learning-workspace/<username>/`。
5. 用户名来源默认使用 `git config user.name`，空格替换为 `-`，失败时回退为 `default-zoom`。
6. 现有 `courses/`、`reference/` 和 `evals/` 是可复用资产，但需要重新组织到平台模块之下。
7. 当前 `rag-learning` 还没有像 `prompt-learning` 那样成熟的脚本层，本次重构需先建立脚本骨架。
8. 本次重构优先目标是建立平台骨架、状态模型、模块边界和任务链条，而不是一次性完成所有代码实现。
9. 涉及 Embedding、Rerank、向量数据库、官方推荐等时效性内容时，后续实现需保留“候选示例而非静态最佳实践”的边界。
10. 当前仓库没有针对 `rag-learning` 的完整自动化测试体系，V1 将以 lint、CLI 输出验证和人工场景验证为主。

## Objective

将现有 `rag-learning` 重构为一个统一的 RAG 系统设计训练平台，包含：

- 平台首页
- 学习中心
- 实战中心
- RAG Lab
- 架构评审
- 学习档案

本次重构要解决的问题：

- 用户当前看到的是 `学习课程 / 实战搭建 / 专题问答` 三路径，产品心智割裂
- `SKILL.md` 过度承载流程规则和交互细节
- 课程、实战、实验、评审之间缺少统一状态与回流机制
- 用户容易停留在“知道概念”，而不是“会选型、会搭建、会评估”
- 企业级方案输出缺少稳定的结构化入口

目标用户：

- 已具备一定编码能力、希望系统掌握 RAG 的工程师
- 需要完成组件选型、最小系统搭建和企业级方案输出的进阶用户

成功应表现为：

- 用户进入 skill 后看到统一平台入口，而不是旧三路径模式
- 用户可在同一状态体系中连续完成学习、实战、实验和评审
- `SKILL.md` 明显变薄，脚本与结构化数据成为流程主承载层
- 持久化信息有明确边界，能够支撑“继续学习”“继续项目”“回看实验”“回看方案”

## Tech Stack

- Python `>=3.11`
- 依赖管理：`uv`
- Lint：`ruff`
- Skill 文档与内容位于仓库内 `agent-skills/rag-learning/` 与 `docs/rag-learning-architecture/`

当前已知相关文件与模块：

- `agent-skills/rag-learning/SKILL.md`
- `agent-skills/rag-learning/courses/`
- `agent-skills/rag-learning/reference/`
- `agent-skills/rag-learning/evals/evals.json`
- `docs/rag-learning-architecture/overview.md`
- `docs/rag-learning-architecture/skill-contract.md`
- `docs/rag-learning-architecture/cli-and-modules.md`
- `docs/rag-learning-architecture/state-model.md`
- `docs/rag-learning-architecture/workspace-and-persistence.md`

建议中的目标脚本结构：

```text
agent-skills/rag-learning/scripts/
  __main__.py
  workspace.py
  state.py
  home.py
  learning.py
  build.py
  lab.py
  review.py
  profile.py
```

## Commands

以下命令是本次重构中建议使用的基础命令：

### Environment

```bash
uv sync
```

### Lint

```bash
ruff check .
```

### Verification-oriented commands

```bash
ruff check .
git diff -- docs/rag-learning-architecture specs/rag-learning agent-skills/rag-learning
```

### Future skill-local examples

```bash
.venv/bin/python -m scripts workspace --bootstrap
.venv/bin/python -m scripts home --dashboard
.venv/bin/python -m scripts learning --catalog
.venv/bin/python -m scripts build --entry-points
.venv/bin/python -m scripts lab --entry-points
.venv/bin/python -m scripts review --entry-points
```

说明：

- 当前 `rag-learning` 尚无对应脚本，以上命令是目标形态表达。
- 具体实现阶段应以最终脚本路径为准，并在落地后补充真实可执行命令。

## Project Structure

本次重构主要涉及以下目录：

```text
agent-skills/rag-learning/
  SKILL.md                     -> skill contract
  courses/                     -> 课程内容源
  reference/                   -> 补充材料
  evals/                       -> 评估样例
  scripts/                     -> 平台脚本实现（待新增）

docs/rag-learning-architecture/
  overview.md                  -> 平台化重构总览
  skill-contract.md            -> SKILL.md 重写依据
  workspace-and-persistence.md -> workspace 与持久化设计
  cli-and-modules.md           -> CLI 和模块边界
  state-model.md               -> 状态模型
  learning-center.md           -> 学习中心设计
  build-center.md              -> 实战中心设计
  rag-lab.md                   -> RAG Lab 设计
  architecture-review.md       -> 架构评审设计
  profile.md                   -> 学习档案设计
  migration-plan.md            -> 迁移计划

specs/rag-learning/
  01-learning-platform-rearchitecture/
    spec.md                    -> 本规格文档
    implementation-plan.md     -> 实施计划
    task-breakdown.md          -> 任务拆解

rag-learning-workspace/
  <username>/                  -> 用户级持久化空间
```

## Code Style

遵循仓库既有规范：

- Python 使用 4 空格缩进
- Markdown / JSON / YAML 使用 2 空格缩进
- UTF-8 / LF
- 不写无意义注释
- 结构优先，避免把流程写死在自然语言里

建议代码风格示例：

```python
from pathlib import Path


def normalize_workspace_username(raw_name: str | None) -> str:
    if raw_name and raw_name.strip():
        return raw_name.strip().replace(" ", "-")
    return "default-zoom"
```

## Testing Strategy

### 当前策略

由于 `rag-learning` 目前主要以文档驱动，本次重构第一阶段以以下验证方式为主：

1. Lint 验证
   - `ruff check .`

2. 结构化 CLI 验证
   - 对新增命令执行最小场景检查
   - 核对 JSON 输出字段、question 结构和状态写入行为

3. 人工流程验证
   - 首页进入
   - 学习中心进入主线课程
   - 实战中心进入最小 RAG
   - RAG Lab 记录实验
   - 架构评审输出方案摘要
   - 学习档案读取

### 测试层级建议

- 单元测试：适合 `workspace.py`、`state.py`、推荐逻辑等纯函数模块
- CLI 集成测试：适合命令输出和 JSON schema 验证
- 人工验证：适合 LLM 参与的课程讲解、实验解释和方案评审

### V1 验收重点

- workspace 是否按预期创建
- 当前状态、课程进度和项目进度是否正确读写
- 首页推荐与 resume 是否与状态一致
- 实验记录是否只保存摘要，不泄漏过程性内容
- 方案摘要是否结构化且可回看

## Boundaries

### Always

- 先更新规格与设计文档，再做结构性实现
- 优先复用现有 `rag-learning` 课程、参考资料和评估资产
- 所有持久化写入都通过 workspace 统一路径管理
- 把 RAG 教学重点放在决策框架、最小实现和实验闭环
- 在实现阶段运行 lint 和最小 CLI 验证

### Ask First

- 大幅重写现有课程体系，例如删除或重排大量课程文件
- 引入新依赖
- 将持久化目录移出项目根目录
- 将 `rag-learning-workspace` 的数据格式改成数据库或外部服务
- 在没有实验依据时把动态候选推荐固化为静态官方榜单

### Never

- 在没有规格的情况下直接进行大规模脚本重构
- 把 `SKILL.md` 继续膨胀成流程手册
- 把临时草稿、中间推理或冗余对话日志写入 workspace
- 把组件选型做成脱离约束的固定排行榜
- 伪造实验结果、推荐依据、进度状态或方案历史

## Success Criteria

当以下条件同时满足时，可认为本次规格对应的重构方向成立：

1. `rag-learning` 的平台心智被明确为：
   - 首页
   - 学习中心
   - 实战中心
   - RAG Lab
   - 架构评审
   - 学习档案

2. `SKILL.md` 的职责被明确收缩为 agent contract，并有对应设计文档支撑。

3. `docs/rag-learning-architecture/` 中存在完整规格和架构文档，可作为后续实现依据。

4. workspace 持久化边界明确：
   - 保存进度、项目摘要、实验结论、评审摘要
   - 不保存中间推理、临时代码草稿和冗余对话

5. 模块边界明确为：
   - `workspace`
   - `home`
   - `learning`
   - `build`
   - `lab`
   - `review`
   - `profile`

6. 后续实现任务能围绕同一依赖链展开：
   - foundation
   - learning/build
   - lab/review
   - profile
   - skill contract switch

## Non-Goals

本 spec 不包含以下内容：

- 一次性写完所有平台脚本实现
- 在 spec 阶段决定所有 Embedding / Rerank / 向量库的“最终推荐”
- 替换现有全部课程内容
- 构建自动化 benchmark 执行器
- 构建复杂考试系统或独立题库

## Completion Definition

本 spec 完成仅表示以下事项已经明确：

- 平台方向稳定
- 架构文档完整
- 实施计划可写
- 任务可拆分并排序

不表示代码已经实现。
