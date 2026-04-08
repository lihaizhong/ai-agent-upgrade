# Spec: Prompt Learning 产品化重构

## Assumptions

以下假设基于当前仓库结构、已有讨论结果和现有 `prompt-learning` skill 状态整理。在进入计划和实施前，默认这些假设成立；如果不成立，应先修订本 spec。

1. 本次工作是对现有 `.opencode/skills/prompt-learning/` 做重构，不是创建一个全新 skill。
2. `prompt-learning` 未来定位为一个学习平台型 skill，而不是保留现有的三模式心智。
3. `SKILL.md` 将被收缩为 agent contract，不再承载主流程和结构细节。
4. 练习和考试题目继续采用“固定蓝图 + LLM 动态出题”模式，不建立静态题库。
5. 用户级持久化数据应统一落在项目根目录下的 `prompt-learning-workspace/<username>/`。
6. 用户名来源默认使用 `git config user.name`，空格替换为 `-`，失败时回退为 `default-zoom`。
7. 本次重构优先目标是建立产品骨架、状态模型和脚本边界，而不是一次性完成全部实现。
8. 当前仓库没有针对 `prompt-learning` 的完整自动化测试体系，V1 将以 lint、CLI 输出验证和人工场景验证为主。

## Objective

将现有 `prompt-learning` 重构为一个统一的学习平台，包含：

- 平台首页
- 学习中心
- 练习中心
- 考试中心
- Prompt Lab
- 学习档案

本次重构要解决的问题：

- 用户当前看到的是 `learn / exam / generate` 三种模式，产品心智割裂
- `SKILL.md` 过度臃肿，同时承担角色说明、流程说明和结构规则
- 状态与持久化能力存在，但还不足以支撑平台连续体验
- 练习、考试、Prompt 生成之间缺少统一入口和回流机制

目标用户：

- 想系统学习提示词工程的学习者
- 已经会一点 prompt，但希望通过课程、练习和实战体系化提升的实践者

成功应表现为：

- 用户进入 skill 后看到统一平台入口，而不是直接暴露底层模式
- 用户可以围绕学习、练习、考试和 Prompt Lab 在同一状态体系内连续使用
- `SKILL.md` 明显变薄，脚本与结构化数据成为流程主承载层
- 持久化信息有明确边界，能够支撑“继续学习”“错题回练”“考试回流”“模板保存”

## Tech Stack

- Python `>=3.11`
- 依赖管理：`uv`
- Lint：`ruff`
- Skill 代码与文档位于仓库内 `.opencode/skills/prompt-learning/` 与 `docs/prompt-learning-architecture/`

当前已知相关文件与模块：

- `.opencode/skills/prompt-learning/SKILL.md`
- `.opencode/skills/prompt-learning/scripts/__main__.py`
- `.opencode/skills/prompt-learning/scripts/engine.py`
- `.opencode/skills/prompt-learning/scripts/state.py`
- `.opencode/skills/prompt-learning/scripts/exam.py`
- `.opencode/skills/prompt-learning/scripts/course_catalog.py`
- `.opencode/skills/prompt-learning/reference/`
- `.opencode/skills/prompt-learning/courses/`

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

### Run Python module in skill

```bash
.venv/bin/python -m .opencode.skills.prompt-learning.scripts
```

说明：

- 上述模块运行命令是目标形态的表达，实际实施时可能仍通过 skill 目录下的相对模块路径运行
- 在具体脚本迁移时，应以当前可执行路径为准，并在实现阶段补充最终命令示例

### Existing skill-local examples

```bash
.venv/bin/python -m scripts learn --list
.venv/bin/python -m scripts exam --structure
.venv/bin/python -m scripts generate --workflow --topic "会议纪要总结"
```

### Verification-oriented commands

```bash
ruff check .
git diff -- docs/prompt-learning-architecture .opencode/skills/prompt-learning
```

## Project Structure

本次重构主要涉及以下目录：

```text
.opencode/skills/prompt-learning/
  SKILL.md                    -> skill contract
  scripts/                    -> 平台脚本实现
  courses/                    -> 课程内容源
  reference/                  -> 补充材料
  code/                       -> 课程示例代码

docs/prompt-learning-architecture/
  overview.md                 -> 产品化重构总览
  skill-contract.md           -> SKILL.md 重写依据
  workspace-and-persistence.md-> workspace 与持久化设计
  cli-and-modules.md          -> CLI 和模块边界
  state-model.md              -> 状态模型
  learning-center.md          -> 学习中心设计
  practice-center.md          -> 练习中心设计
  exam-center.md              -> 考试中心设计
  prompt-lab.md               -> Prompt Lab 设计
  migration-plan.md           -> 迁移计划

specs/prompt-learning/
  01-learning-platform-rearchitecture/
    spec.md                  -> 本规格文档

prompt-learning-workspace/
  <username>/                 -> 用户级持久化空间
```

建议中的目标脚本结构：

```text
.opencode/skills/prompt-learning/scripts/
  __main__.py
  workspace.py
  home.py
  state.py
  learning.py
  practice.py
  exam.py
  prompt_lab.py
  profile.py
  course_catalog.py
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

这段示例体现本次重构期望的风格：

- 命名直接
- 单一职责
- 输入输出清晰
- 不做隐式魔法

## Testing Strategy

### 当前策略

由于 `prompt-learning` 目前主要以脚本和文档驱动，本次重构第一阶段以以下验证方式为主：

1. Lint 验证
   - `ruff check .`

2. 结构化 CLI 验证
   - 对新增或迁移的命令执行最小场景检查
   - 核对 JSON 输出字段、question 结构和状态写入行为

3. 人工流程验证
   - 首页进入
   - 继续学习
   - 课后练习
   - Prompt Lab 生成与保存模板
   - 读取学习档案

### 测试层级建议

- 单元测试：适合 `workspace.py`、`state.py`、纯函数型推荐逻辑
- CLI 集成测试：适合命令输出和 JSON schema 验证
- 人工验证：适合 LLM 参与的教学讲解、动态出题和 Prompt Lab 交互

### V1 验收重点

- workspace 是否按预期创建
- 当前状态和课程进度是否正确读写
- 首页推荐与 resume 是否与状态一致
- Prompt Lab 保存模板时是否只保存确认后的结果
- 练习和考试是否仍保持“结构固定、内容动态”

## Boundaries

### Always

- 先更新规格与设计文档，再做结构性实现
- 优先复用现有 `prompt-learning` 课程、考试和脚本资产
- 所有持久化写入都通过 workspace 统一路径管理
- 练习与考试坚持“蓝图固定、题目动态”
- 在实现阶段运行 lint 和最小 CLI 验证

### Ask First

- 修改课程体系本身，例如删改 17 门课结构
- 引入新依赖
- 大幅更改考试题数、题型、分值设计
- 将持久化目录移出项目根目录
- 将 `prompt-learning-workspace` 中的数据格式改成数据库或外部服务

### Never

- 在没有规格的情况下直接进行大规模脚本重构
- 把 `SKILL.md` 继续膨胀成流程手册
- 把临时草稿、中间推理或冗余对话日志写入 workspace
- 用静态题库替代动态出题机制
- 伪造进度、考试结果、推荐依据或模板保存状态

## Success Criteria

当以下条件同时满足时，可认为本次规格对应的重构方向成立：

1. `prompt-learning` 的平台心智被明确为：
   - 首页
   - 学习中心
   - 练习中心
   - 考试中心
   - Prompt Lab
   - 学习档案

2. `SKILL.md` 的职责被明确收缩为 agent contract，并有对应设计文档支撑。

3. `docs/prompt-learning-architecture/` 中存在完整规格和架构文档，可作为后续实现依据。

4. workspace 持久化边界明确：
   - 保存进度、错题、考试结果、已确认模板
   - 不保存临时草稿和中间推理

5. 新 CLI 边界明确，至少覆盖：
   - `workspace`
   - `home`
   - `learning`
   - `practice`
   - `exam`
   - `lab`
   - `profile`

6. 迁移计划明确，能够以阶段化方式从旧结构平滑迁移到新结构，而不是一次性推翻重写。

## Open Questions

以下问题仍建议在进入实施前最终确认：

1. `prompt-learning-workspace/` 是否需要加入仓库级文档说明，例如更新 `README.md` 或 `AGENTS.md`？
2. 首页推荐逻辑在 V1 是否仅采用规则驱动，还是要同步定义更明确的优先级配置文件？
3. `profile.py` 在 V1 是否只做聚合读取，还是同时承担部分推荐逻辑？
4. 是否要为 `workspace.py` 和 `state.py` 补充最小自动化测试，还是先以 CLI 验证和人工验证为主？
5. 旧 `learn / exam / generate` 兼容层预计保留到哪个阶段再做清理？
