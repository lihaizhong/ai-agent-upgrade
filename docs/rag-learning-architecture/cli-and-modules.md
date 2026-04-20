# RAG Learning CLI 与模块设计

## 目标

将 `rag-learning` 的脚本层从“围绕学习 / 实战 / 问答的轻路由”升级为“围绕平台模块的结构化 CLI”。

重构后，脚本应体现平台边界，而不是继续让首页、实战推进、实验记录和方案评审混在一起。

## 建议的顶层命令

建议正式支持以下一级命令：

- `workspace`
- `home`
- `learning`
- `build`
- `lab`
- `review`
- `profile`

对应产品模块：

- `workspace`：用户空间初始化与路径解析
- `home`：平台首页与推荐
- `learning`：学习中心
- `build`：实战中心
- `lab`：RAG Lab
- `review`：架构评审
- `profile`：学习档案

## 设计原则

### 平台化命名

命令命名应对应产品模块，而不是暴露旧模式心智。

### 结构化输出

脚本应返回：

- 导航卡片
- 结构化问题
- 固定步骤面板
- 实验蓝图
- 评审模板
- 状态摘要

而不是只返回自然语言说明。

### 内容层与结构层分离

脚本负责结构，LLM 负责内容。

### 配置源单一

平台运行时结构优先来自统一配置源，而不是分散在 Markdown、脚本硬编码和自然语言说明中。

建议职责如下：

- `reference/catalog.md`：学习目录、课程主线、模块映射
- `reference/platform-config.json`：`build / lab / review` 的结构化运行配置
- `courses/`：教学正文，不承担运行期结构配置职责

## `workspace` 模块

### 职责

- 解析 git 用户名
- 规范化 workspace 用户名
- 定位 workspace 根目录
- 初始化目录和最小文件集

### 建议命令

- `workspace --resolve-user`
- `workspace --show-root`
- `workspace --bootstrap`

## `home` 模块

### 职责

- 返回首页 dashboard
- 生成推荐动作
- 返回继续上次进度的目标

### 建议命令

- `home --dashboard`
- `home --resume`
- `home --recommend`

### `home --resume` 输出语义

`home --resume` 应返回 continuation contract，而不是仅透传原始状态字段。

最小上应明确：

- `resume_action`
- `target_module`
- `target_payload`
- `reason`
- `is_fallback`

### 首页主导航卡片

V1 固定四张：

- 继续学习
- 搭建最小 RAG
- 进入 RAG Lab
- 发起架构评审

学习档案作为次级入口，不放进首页主卡片。

## `learning` 模块

### 职责

- 课程目录
- 学习路径推荐
- 课程元数据
- 课程面板
- 课程完成状态更新

### 建议命令

- `learning --catalog`
- `learning --path --level <novice|intermediate|advanced|enterprise>`
- `learning --recommend-course`
- `learning --lesson-meta --course <N>`
- `learning --lesson-panel --course <N>`
- `learning --complete --course <N>`

### 说明

`lesson-meta` 只返回课程路径和元数据，讲解内容由 LLM 读取课程文件后组织生成。

## `build` 模块

### 职责

- 返回实战入口
- 维护实战阶段结构
- 推进最小 RAG 搭建
- 记录当前项目结果

### 建议命令

- `build --entry-points`
- `build --resume`
- `build --scenario <name>`
- `build --step-panel --project <id> --step <name>`
- `build --record-step`
- `build --summary`

### V1 实战入口

- 本地最小 RAG
- 客服机器人 RAG
- 企业知识库搜索

V1 只要求完整做通第一个入口，其余可先作为设计预留。

### `build --resume`

当存在进行中的 project 时，应返回当前 project 与最小恢复上下文。

当不存在进行中的 project 时，应显式回退到 build entry points，而不是伪造当前步骤。

## `lab` 模块

### 职责

- 返回实验入口
- 构建实验蓝图
- 记录实验结果
- 聚合实验历史

### 建议命令

- `lab --entry-points`
- `lab --blueprint --topic <embedding|rerank|chunking|hybrid>`
- `lab --resume`
- `lab --record-result`
- `lab --history`

### V1 实验入口

- Embedding 对比
- Rerank 是否值得引入
- Chunk size / top-k 对比

### `lab --resume`

当存在当前实验主题时，应返回 topic 与最小 handoff context。

当不存在当前实验主题时，应显式回退到 lab entry points。

## `review` 模块

### 职责

- 获取架构评审入口
- 生成评审模板
- 记录评审摘要
- 输出后续优化建议

### 建议命令

- `review --entry-points`
- `review --template --scenario <name>`
- `review --record-summary`
- `review --history`

### V1 评审入口

- 新建方案评审
- 继续最近评审
- 查看历史方案摘要

## `profile` 模块

### 职责

- 汇总学习档案
- 展示当前进度
- 展示实验历史、选型偏好和评审摘要

### 建议命令

- `profile --summary`
- `profile --progress`
- `profile --experiments`
- `profile --reviews`

## 输出设计原则

### 首页与入口

优先返回卡片式或 selector 友好的结构，而不是纯文本菜单。

### 实战与实验

每一轮输出至少包含：

- 当前决策
- 推荐方案
- 取舍理由
- 当前任务
- 下一步入口

当需要跨模块回流时，脚本应显式输出 handoff 字段，而不是只依赖隐式当前状态。

### 评审

每一轮输出至少包含：

- 当前场景
- 已知约束
- 当前待定事项
- 推荐结论
- 未决风险

## V1 范围

CLI V1 先做：

- `workspace`
- `home`
- `learning`
- `build`
- `lab`
- `review`
- `profile`

暂不保留旧 `学习 / 实战 / 专题问答` 作为脚本接口。
