# Spec Change: Config Source Unification And Module Handoff

## Objective

把 `rag-learning` 从“部分文档解析 + 部分硬编码”的平台实现，收敛为“配置源单一、模块 handoff 明确、状态回流可验证”的结构。

本次 change 主要解决：

1. 课程与场景元数据来自 Markdown 解析，而 build project / step panel 又硬编码在脚本中
2. `lab` 和 `review` 有配置源，但 `build` 没有与之对齐
3. build -> lab -> review 的 handoff 目前更多依赖隐式上下文，而不是显式字段
4. 多处真相并存会导致文档、代码、测试长期漂移

## Assumptions

1. `reference/catalog.md`、`reference/platform-config.json` 和现有课程文件都是可复用资产
2. 本次 change 的目标是统一配置边界，而不是重写全部课程内容
3. `build`、`lab`、`review` 都需要稳定的结构化定义
4. 模块之间允许保留轻量 handoff 数据，但不保存冗余过程日志

## Background

当前实现中：

- `catalog.py` 从 `reference/catalog.md` 解析课程和场景
- `build.py` 自己定义 `PROJECT_OVERRIDES` 与 `STEP_PANELS`
- `lab.py` 从 `platform-config.json` 读取 topic 配置
- `review.py` 也从 `platform-config.json` 读取 scenario 配置

这意味着当前至少存在三类配置来源：

1. Markdown 表格
2. JSON 配置
3. Python 硬编码常量

短期内能跑，但后续一旦扩项目、补实验、加评审模板，就会形成明显的双真相甚至三真相。

## Scope

### 1. 为 build 引入结构化配置源

将以下定义从 `build.py` 抽离到统一配置源：

- project metadata
- step sequence
- step panel fields
- competency mapping
- recommended next step

目标不是追求“全都 JSON 化”，而是让 build 与 lab/review 一样拥有稳定配置边界。

### 2. 统一平台配置入口

需要明确：

- 哪些信息属于 `catalog`
- 哪些信息属于 `platform-config`
- 哪些信息属于课程正文

建议原则：

- `catalog`: 面向学习目录与模块映射
- `platform-config`: 面向 build / lab / review 等结构化运行配置
- `courses/`: 面向教学正文

### 3. 定义模块 handoff contract

至少明确以下 handoff：

- learning -> build
- build -> lab
- build -> review
- lab -> review
- lab/review -> profile

handoff 应是结构化字段，而不是隐式依赖“当前模块里恰好写过某个状态”。

例如：

- 当前 project id
- 当前 step
- 推荐进入的 lab topic
- 可引用的 experiment summary ids
- review 可消费的 evidence summary

### 4. 收紧状态与配置之间的校验

需要增加配置层校验，避免以下问题：

- `catalog` 中存在场景，但 `build` 配置缺失
- step 的 `next_step` 指向不存在节点
- lab / review 引用不存在的 competency area
- handoff 字段写入了无效枚举

### 5. 对齐文档与测试

需要更新：

- `docs/rag-learning-architecture/cli-and-modules.md`
- `docs/rag-learning-architecture/build-center.md`
- `docs/rag-learning-architecture/rag-lab.md`
- `docs/rag-learning-architecture/architecture-review.md`
- 对应测试

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_config_units
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.rag_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/rag-learning/scripts tests/rag_learning
```

## Project Structure

- `agent-skills/rag-learning/scripts/catalog.py`
  - 学习目录解析与课程映射
- `agent-skills/rag-learning/scripts/config.py`
  - 平台结构化配置加载
- `agent-skills/rag-learning/scripts/build.py`
  - project / step 编排
- `agent-skills/rag-learning/scripts/lab.py`
  - experiment blueprint 与 result handoff
- `agent-skills/rag-learning/scripts/review.py`
  - review template 与 evidence 消费
- `agent-skills/rag-learning/scripts/state.py`
  - handoff 与状态回流
- `agent-skills/rag-learning/reference/catalog.md`
- `agent-skills/rag-learning/reference/platform-config.json`
- `docs/rag-learning-architecture/`
- `tests/rag_learning/`

## Code Style

优先做“配置边界清晰 + 校验直接”的实现，不把配置系统做成复杂框架。

```python
def load_build_projects(skill_dir: Path) -> dict[str, dict]:
    config = load_platform_config(skill_dir)
    return config.get("build_projects", {})
```

约束：

- 配置加载逻辑尽量单层
- 业务脚本不再重复携带大型硬编码结构
- 校验要在加载期尽早失败

## Testing Strategy

- 为配置完整性增加单元测试
- 为 handoff 和状态回流增加流程测试
- 至少覆盖以下场景：
  - build project 与 catalog 场景映射一致
  - step graph 不存在断裂或悬空 next step
  - lab / review topic 与 competency area 有效
  - 从 build 进入 lab，再进入 review 时，关键 handoff 字段正确

## Boundaries

- Always:
  - 保持配置源职责清晰
  - 让模块 handoff 可结构化、可测试
  - 用校验避免多处真相继续扩散
- Ask first:
  - 把全部 Markdown 课程元数据迁移成数据库
  - 引入复杂配置框架
  - 大改课程正文组织方式
- Never:
  - 继续在脚本里堆积大型硬编码面板
  - 让 handoff 只依赖隐式状态猜测
  - 允许配置缺口通过默认值静默吞掉

## Success Criteria

- [x] build 拥有与 lab/review 一致的结构化配置边界
- [x] `catalog`、`platform-config`、`courses` 的职责被明确区分
- [x] build -> lab -> review 的 handoff 字段被定义并落到状态或结果结构中
- [x] 配置缺失、非法枚举、断裂 step graph 会在测试中暴露
- [x] 主要架构文档与代码配置源一致

## Non-Goals

- 不重写全部课程
- 不引入数据库或远程配置中心
- 不新增平台模块
- 不把状态层改造成复杂工作流引擎

## Open Questions

1. `build` 配置应并入现有 `platform-config.json`，还是拆成独立 `build-config.json`？
2. experiment / review history 是否需要引入稳定的 summary id 以支持显式 evidence handoff？
