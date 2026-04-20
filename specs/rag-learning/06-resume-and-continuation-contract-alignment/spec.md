# Spec Change: Resume And Continuation Contract Alignment

## Objective

收敛 `rag-learning` 的“继续上次进度”产品语义，使首页恢复、模块内恢复和近期上下文回流形成一致 contract，而不是停留在原始状态回显。

本次 change 主要解决：

1. `home --resume` 当前只回显 `current-state.json` 的原始字段，不是可执行 continuation contract
2. 架构文档已声明 `build --resume`、`lab --resume` 等产品面，但 CLI 和脚本尚未实现
3. `review` 文档中的“继续最近评审 / 查看历史摘要”仍未进入真实入口结构
4. 用户完成一次 build / lab / review 后，平台虽然记住了状态，但还没有稳定的“下一次回来怎么继续”协议

## Assumptions

1. `rag-learning` 仍维持现有平台模块：
   - `home`
   - `learning`
   - `build`
   - `lab`
   - `review`
   - `profile`
2. continuation contract 服务的是产品恢复与导航，不是引入新的会话工作流引擎
3. 当前 `current-state.json`、`build-progress.json`、实验/评审 history 仍是恢复语义的主要数据源
4. 本次 change 不重做首页推荐逻辑，只聚焦“继续 / 恢复”语义

## Background

当前平台已经具备推荐动作与模块 handoff，但恢复语义仍然偏弱：

- `home --resume` 只返回 `resume_target`，没有声明“继续动作是什么”
- `build` 和 `lab` 文档中都有 `--resume`，但真实 CLI 尚未提供
- `review --entry-points` 仍只返回 scenario 列表，没有“继续最近评审”或“查看历史摘要”的产品入口
- 结果是平台知道“当前记住了什么”，却没有把这些信息变成稳定的继续入口

这会让用户第二次进入 skill 时重新回到解释态，而不是直接恢复到可推进的下一步。

## Scope

### 1. 让 `home --resume` 返回可执行 continuation contract

`home --resume` 不应只暴露原始状态，而应明确给出：

- 当前最应该恢复到哪个模块
- 当前恢复动作是什么
- 恢复所需的最小上下文字段
- 没有可恢复上下文时的明确 fallback

例如：

- `resume_action = continue_learning`
- `resume_action = continue_build`
- `resume_action = continue_lab`
- `resume_action = continue_review`
- 或回退到首页主入口

### 2. 为 `build` / `lab` 提供模块内 resume surface

产品层应允许用户在模块内直接恢复，而不是总是先回首页再人工拼接上下文。

至少需要支持：

- `build --resume`
- `lab --resume`

它们应优先返回当前进行中的 project / topic 的最小恢复信息；没有上下文时回到模块入口。

### 3. 让 `review` 暴露 continuation-aware 入口

`review` 当前不一定需要独立 `--resume`，但入口层至少应能表达：

- 发起新的评审
- 继续最近一次评审
- 查看最近历史摘要

这样首页或 agent 才能把“继续评审”真正落到结构化入口，而不是只靠自然语言解释。

### 4. 明确 continuation 的优先级

恢复顺序应可解释，例如：

1. 显式当前模块上下文
2. 进行中的 build / lab / review
3. 最近一次可继续的上下文
4. 回退到模块入口或首页

平台不应因为状态文件里有任意历史字段，就伪造一个“正在继续”的恢复动作。

### 5. 对齐文档、CLI 和测试

需要把以下几层对齐成单一真相：

- `cli-and-modules.md`
- `state-model.md`
- `build-center.md`
- `rag-lab.md`
- `architecture-review.md`
- `tests.rag_learning`

## Boundaries

- Always:
  - continuation 必须返回可执行动作，而不是原始状态字段堆叠
  - 没有上下文时必须显式回退到入口，而不是假装“可继续”
  - 首页恢复与模块内恢复必须共享同一套上下文判断逻辑
- Ask first:
  - 引入新的顶层产品模块
  - 新增复杂会话恢复系统或任务队列
  - 让 continuation 保存长篇会话正文
- Never:
  - 让 `home --resume` 只做状态透传
  - 让文档承诺的 `--resume` surface 长期停留在未实现状态
  - 用模糊自然语言代替结构化 continuation contract

## Success Criteria

- [x] `home --resume` 返回稳定、可执行的 continuation contract
- [x] `build --resume` 能恢复当前 project 和下一步上下文，或显式回退到 entry points
- [x] `lab --resume` 能恢复当前 topic 和 handoff context，或显式回退到 entry points
- [x] `review` 入口能表达“新建 / 继续最近 / 查看历史摘要”三类产品动作
- [x] continuation 优先级在代码、文档和测试中一致
- [x] `tests.rag_learning` 对应恢复流回归通过

## Non-Goals

- 不重做首页推荐策略
- 不引入新的状态存储后端
- 不扩展新的学习或实战模块
- 不把所有 continuation 都做成 selector

## Open Questions

1. `review` 是否也应该最终补成独立 `review --resume`，还是先维持 continuation-aware entry points 即可？
2. `home --resume` 应保持 `open_ended`，还是升级为带明确 action payload 的 `inform` 输出更合适？
