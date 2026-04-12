# Spec Change: Workspace Hardening And State Alignment

## Objective

在保留 `defaults` fallback 的前提下，修复 `prompt-learning` 当前暴露出的四类问题：

1. workspace 用户名与报告文件名缺少路径安全约束
2. fallback 行为在 skill/doc/spec/test 之间没有单一真相
3. 首页推荐没有真正消费 `current-state.json` 中的推荐动作
4. 错题回练、掌握度统计与 Prompt Lab 模板保存边界存在产品语义断裂

本次 change 的目标不是扩展产品能力，而是把现有平台行为收敛为一致、可解释、可验证的系统。

## Background

当前代码已经引入 `prompt-learning-workspace/defaults/` 作为 `git config user.name` 不可用时的 fallback workspace。

但仓库中仍同时存在三种互相冲突的真相：

1. `workspace.py` 与 `09-workspace-fallback` spec：允许 fallback
2. `SKILL.md` 与架构文档：要求 identity 缺失时直接失败
3. `tests/prompt_learning/`：同时存在“应该 fallback”与“应该失败”的互斥断言

与此同时，review 还暴露出几个实现级问题：

- 用户名直接拼接路径，可能造成越界写文件
- 首页推荐忽略显式 `recommended_next_action`
- 错题回练能关闭错题，但 mastery 只累计不回收
- Prompt Lab 保存模板只校验非空，没守住“先校验、再确认、再保存”的边界

## Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_platform
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_state_flow
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_exam_session
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest tests.prompt_learning.test_workspace_fallback
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check agent-skills/prompt-learning/scripts tests/prompt_learning
```

## Project Structure

- `agent-skills/prompt-learning/scripts/`
  - `workspace.py`: workspace 身份解析、目录和文件初始化
  - `home.py`: 首页推荐与导航
  - `practice.py`: 练习记录、错题状态、错题回练
  - `state.py`: 当前状态和长期进度摘要
  - `prompt_lab.py`: Prompt Lab 校验与模板保存
  - `exam.py`: 报告生成与考试历史写入
- `agent-skills/prompt-learning/SKILL.md`
  - skill contract，定义产品行为与持久化边界
- `docs/prompt-learning-architecture/`
  - 平台架构与状态模型设计文档
- `tests/prompt_learning/`
  - prompt-learning CLI 与状态流回归测试

## Code Style

保持现有 Python 代码风格，避免引入新依赖；路径和状态判断优先用直接、可解释的实现，而不是抽象层叠。

```python
def sanitize_workspace_component(raw_name: str | None) -> str:
    if not raw_name or not raw_name.strip():
        return DEFAULT_WORKSPACE_USERNAME

    candidate = raw_name.strip().replace(" ", "-")
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", candidate)
    safe = safe.strip(".-")
    return safe or DEFAULT_WORKSPACE_USERNAME
```

约束：

- 路径组件必须是稳定、可预期的安全值
- 推荐逻辑必须优先尊重显式状态，再做兜底推断
- 持久化逻辑必须与文档中的产品语义一致

## Testing Strategy

- 单元/CLI 集成测试继续放在 `tests/prompt_learning/`
- 采用 bug-first 回归方式：先补失败测试，再改实现
- 新测试重点覆盖：
  - fallback 成为唯一身份策略
  - 恶意用户名不会逃逸 workspace 根目录
  - 首页推荐会消费 `recommended_next_action`
  - 错题 resolved 后 mastery 会同步改善
  - Prompt Lab 未校验/未确认模板不能保存

## Boundaries

- Always:
  - 保留 `defaults fallback` 作为 workspace identity 缺失时的唯一产品行为
  - 通过测试证明每个修复点已被覆盖
  - 让文档、spec、测试、代码表达同一行为
- Ask first:
  - 修改 workspace 目录层级
  - 引入新依赖
  - 扩大 Prompt Lab schema
- Never:
  - 回退到“identity 缺失直接失败”的旧行为
  - 允许未经净化的用户名参与目录或文件名拼接
  - 未经确认就持久化 Prompt Lab 草稿

## Success Criteria

- [ ] `defaults fallback` 成为 skill、doc、spec、test、code 的单一真相
- [ ] 任意用户名输入都不能写出 `prompt-learning-workspace/` 和 `exam/reports/` 预期范围之外
- [ ] 首页推荐可正确返回 `review_mistakes`、`review_weak_topics`、`continue_exam` 等显式动作
- [ ] 错题回练成功后，`mistakes.jsonl` 与 `mastery.json` 不再相互矛盾
- [ ] Prompt Lab 只有在槽位完整、草稿审查通过、用户确认后才会保存模板
- [ ] `tests.prompt_learning` 全绿，`ruff check` 通过

## Non-Goals

- 不重构 CLI 结构
- 不改变考试蓝图、练习题型或课程内容
- 不把 workspace 改成数据库
- 不引入复杂掌握度评分模型

## Open Questions

- 错题回练对 mastery 的修正规则采用“按 resolved 标签抵扣有效错误数”，作为本次 change 的默认实现；若后续需要更复杂模型，再单独起 spec change。
