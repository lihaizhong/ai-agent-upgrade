# Spec Change: Build Progression And Completion Semantics

## Objective

收敛 `rag-learning` 实战中心的步骤推进与完成态语义，使 build 真正成为“可推进、可完成、可回流”的产品模块，而不是只记录已发生步骤。

本次 change 主要解决：

1. `record_build_step()` 当前把 `current_step` 写成刚完成的 step，而不是下一步可执行 step
2. project status 目前几乎不会进入 `completed`，导致完成态和档案统计失真
3. build 完成关键步骤后，`recommended_next_action` 总是近似写成 `continue_build`，没有消费 step handoff 语义
4. 首页、档案和后续恢复逻辑因此拿不到真实的“下一步应该继续哪里”

## Assumptions

1. V1 仍只要求完整做通 `local-minimum-rag` 主线
2. build step graph 仍来自 `platform-config.json`
3. 本次 change 以“阶段推进和完成态语义”优先，不引入复杂工作流引擎
4. lab / review handoff 已经存在结构化字段，本次 change 主要让 build 真正消费并落盘这些信息

## Background

当前实战中心已经有 step panel 和 handoff 字段，但推进语义仍然偏弱：

- 用户完成 `embedding` 后，状态里仍把 `current_step` 记成 `embedding`
- 即使已经完成 `evaluation`，project 也可能继续保持 `in_progress`
- step panel 配置中的 `handoff` 主要停留在返回值里，没有沉淀成状态层或完成态语义

这会影响：

- `build --resume` 无法恢复到真正下一步
- `profile` 无法区分 active project 和 completed project
- `home --recommend` 很难基于 build 完成态做正确建议

## Scope

### 1. 让 build progress 指向“下一步可执行状态”

完成某个 step 后，状态层应能表达：

- 刚完成了什么
- 下一步是什么
- 当前 project 是否仍在进行中

最小要求：

- `completed_steps` 继续保留
- `current_step` 指向下一步，而不是刚完成的 step
- 如有必要，可增加 `last_completed_step`

### 2. 引入真实的 project completed 语义

当用户完成最终 step 时，project 应进入真实完成态，例如：

- `status = completed`
- `completed_at`
- `current_step = null` 或明确的完成哨兵值

这层语义必须能被 `profile`、`resume` 和首页推荐稳定消费。

### 3. 让 build completion 消费 step handoff

step 完成后，状态层不应一律写成 `continue_build`。

需要支持两类结果：

- 继续 build 主线
- 进入 lab / review 等跨模块 handoff

也就是说，step panel 中的：

- `recommended_action`
- `recommended_module`
- `recommended_topic`
- `recommended_scenario`

不应只停留在返回 payload，而应影响状态层记录的下一步动作。

### 4. 对齐 build、home、profile 的完成态解释

至少需要保证：

- build 自己知道 project 是否完成
- profile 不把 completed project 继续算成 active
- home 在 project 完成后不会继续给出“继续 build”这类过期动作

## Boundaries

- Always:
  - `current_step` 必须表达下一步可执行状态
  - final step 完成后必须进入真实 completed 语义
  - build handoff 不能只存在于展示层
- Ask first:
  - 引入多项目并行调度器
  - 把 build 改造成复杂工作流引擎
  - 扩大到大量新项目与分支图
- Never:
  - 让 completed project 长期停留在 `in_progress`
  - 让首页继续推荐用户回到已经完成的 build step
  - 让状态层忽略已有 handoff 配置

## Success Criteria

- [ ] `build-progress.json` 中的 `current_step` 指向下一步可执行 step，而不是刚完成的 step
- [ ] 最终 step 完成后 project 会进入真实 `completed` 状态
- [ ] build step 完成会消费 step handoff，写入正确的下一步动作语义
- [ ] `profile` 不再把 completed project 算作 active project
- [ ] `home` 在 build 完成或跨模块 handoff 后不会继续给出过期的 `continue_build`
- [ ] 相关平台、状态流和配置测试覆盖上述行为

## Non-Goals

- 不新增复杂的 build UI
- 不重做全部项目图谱
- 不把 lab / review 的全部状态模型并入 build
- 不实现自动代码执行或自动 benchmark

## Open Questions

1. final step 完成后，默认动作应优先进入 `open_lab`、`start_review`，还是回到首页重新判断？
2. `current_step` 在 completed 状态下应为 `null` 还是稳定哨兵值（如 `completed`）？
