# RAG Lab 设计

## 目标

将零散的“选型讨论”重构为平台中的 `RAG Lab` 模块，使其承担“通过对比实验形成工程判断”的职责。

RAG Lab 的核心目标不是输出一份排行榜，而是：

- 让用户围绕单个变量做对比
- 记录实验条件和结果
- 形成可复用的结论
- 把结论回流到实战和评审

## 产品定位

RAG Lab 是 `rag-learning` 的实验室模块。

它适合：

- 比较两种 embedding
- 判断是否需要 rerank
- 比较 chunking / top-k / hybrid search 的影响
- 验证精度、延迟、成本的取舍

它不等同于普通问答，也不等同于通用 benchmark 展示器。

## 核心流程

RAG Lab 建议采用以下固定流程：

1. 明确实验目标
2. 选择实验主题
3. 确定对比变量
4. 固定评估维度
5. 执行最小对比
6. 汇总结果
7. 形成结论
8. 回流到实战或评审

## V1 实验主题

V1 保持三个固定实验，不扩展更多：

- `embedding`
- `rerank`
- `chunking`

后续可扩展：

- `hybrid`
- `metadata-filtering`
- `citation`

## 实验蓝图

每个实验都应使用固定蓝图，避免对比过程失控。

建议字段：

```json
{
  "topic": "embedding",
  "goal": "比较两种 embedding 在当前语料上的检索表现",
  "variables": [
    "model_a",
    "model_b"
  ],
  "fixed_conditions": [
    "same_corpus",
    "same_chunking",
    "same_top_k"
  ],
  "metrics": [
    "hit_rate_at_5",
    "latency",
    "cost"
  ],
  "output_fields": [
    "result_summary",
    "recommended_choice",
    "tradeoff_note"
  ]
}
```

## 交互原则

### 一次只比较一个变量

不要把 embedding、chunking 和 rerank 混在同一次实验里。

### 优先使用用户当前项目语料

如果用户已在实战中心推进，应优先复用当前项目场景，而不是抽象示例。

### 结果必须带上下文

实验结论必须明确：

- 在什么数据与场景下成立
- 主要收益是什么
- 成本是什么

### 实验之后必须给结论

不要停留在“各有优缺点”。

## 与实战中心的关系

RAG Lab 不是独立玩法，应该服务于实战推进。

典型联动：

- 实战中的 embedding 纠结 -> 进入 `embedding` 实验
- 实战中的精度不足 -> 进入 `rerank` 或 `chunking` 实验
- 实验结束 -> 返回当前 build step

因此实验蓝图和实验结果都应保留最小 handoff context，例如：

- 来源模块
- 当前 project id
- 当前 build step
- 回流动作

## 与架构评审的关系

RAG Lab 的结论可以作为评审依据，但不能直接替代完整架构评审。

例如：

- “在当前中文语料上 bge-m3 召回更稳”

这可以作为选型证据，但还不能回答企业部署、安全、治理问题。

## CLI 建议

RAG Lab 对应 `lab` 模块，建议支持：

- `lab --entry-points`
- `lab --blueprint --topic <embedding|rerank|chunking>`
- `lab --resume`
- `lab --record-result`
- `lab --history`

`lab --resume` 应优先恢复当前实验主题与最小 handoff context；如果没有当前实验上下文，则显式回退到实验入口。

## 数据职责划分

### 脚本负责

- 实验入口
- 实验蓝图
- 固定评估字段
- 结果记录
- 历史聚合
- 向评审暴露可消费的 evidence summary

### LLM 负责

- 实验目标澄清
- 变量建议
- 结果解读
- 推荐结论表达

## V1 范围

RAG Lab V1 先做：

- 三类实验主题
- 固定实验蓝图
- 实验结果记录
- 实验历史回看

暂不做：

- 自动 benchmark 执行器
- 大规模离线评测系统
- 多数据集统一排行榜
