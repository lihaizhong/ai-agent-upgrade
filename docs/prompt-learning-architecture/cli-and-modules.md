# Prompt Learning CLI 与模块设计

## 目标

将 `prompt-learning` 的脚本层从“围绕旧模式的命令集合”升级为“围绕产品模块的结构化 CLI”。

重构后，脚本应体现产品边界，而不是继续把首页、学习、练习、考试和生成逻辑混在一起。

## 当前状态

这份 CLI 设计已经落地。

当前正式支持的顶层命令只有：

- `workspace`
- `home`
- `learning`
- `practice`
- `exam`
- `lab`
- `profile`

旧 `mode / learn / generate / state` 已移除，不再作为兼容接口保留。

## 顶层命令设计

建议引入以下一级命令：

- `home`
- `workspace`
- `learning`
- `practice`
- `exam`
- `lab`
- `profile`

对应产品模块：

- `home`：平台首页与推荐
- `workspace`：用户空间初始化与路径解析
- `learning`：学习中心
- `practice`：练习中心
- `exam`：考试中心
- `lab`：Prompt Lab
- `profile`：学习档案

## 设计原则

### 平台化命名

命令命名应对应产品模块，而不是暴露旧的内部模式心智。

### 结构化输出

脚本应返回：

- 导航卡片
- 结构化问题
- 固定蓝图
- 状态摘要
- 路由目标

而不是仅返回自然语言说明。

### 内容层与结构层分离

脚本负责结构，LLM 负责内容。

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

### 首页主导航卡片

V1 固定四张：

- 继续学习
- 开始练习
- 参加考试
- 进入 Prompt Lab

学习档案作为次级入口，不放进首页主卡片。

## `learning` 模块

### 职责

- 课程目录
- 类别浏览
- 课程元数据
- 课后面板
- 代码讲解结构
- 课程完成状态更新

### 建议命令

- `learning --catalog`
- `learning --category <name>`
- `learning --recommend-course`
- `learning --lesson-meta --course <N>`
- `learning --lesson-panel --course <N>`
- `learning --code-meta --course <N>`
- `learning --code-outline --course <N>`
- `learning --complete --course <N>`

### 说明

`lesson-meta` 只返回课程路径和元数据，讲解内容由 LLM 读取课程文件后组织生成。

## `practice` 模块

### 职责

- 返回练习入口
- 构建动态练习蓝图
- 记录练习结果
- 管理错题回练
- 输出练习摘要

### 建议命令

- `practice --entry-points`
- `practice --resume`
- `practice --blueprint --course <N> --mode <current|targeted|mistake>`
- `practice --review-mistakes`
- `practice --record-result`
- `practice --summary`

### V1 练习入口

- 当前课程继续练
- 专项练习
- 错题回练

### 核心原则

题目内容动态生成，但蓝图结构、题型约束和记录 schema 固定。

## `exam` 模块

### 职责

- 返回考试入口
- 返回考试结构与题位蓝图
- 负责题目结构校验
- 维护考试会话中的题目与答案提交
- 生成考试报告

### 建议命令

- `exam --entry-points`
- `exam --structure --type <diagnostic|final>`
- `exam --blueprint --type <diagnostic|final>`
- `exam --start --type <diagnostic|final>`
- `exam --current-question --session <id>`
- `exam --submit-question --session <id>`
- `exam --submit-answer --session <id>`
- `exam --resume`
- `exam --abandon --session <id>`
- `exam --finish --session <id>`
- `exam --validate-mc`
- `exam --validate-fill`
- `exam --validate-essay`
- `exam --validate-paper`
- `exam --report`

### V1 考试入口

- 诊断考试
- 综合考试
- 查看最近考试记录

## `lab` 模块

### 职责

- Prompt Lab 工作流
- 槽位收集与校验
- 审查清单输出
- 模板保存与列表展示

### 建议命令

- `lab --workflow --topic "<topic>"`
- `lab --interview-blueprint --topic "<topic>"`
- `lab --validate-slots --topic "<topic>"`
- `lab --review-checklist --topic "<topic>"`
- `lab --validate-draft --topic "<topic>"`
- `lab --save-template`
- `lab --list-templates`

## `profile` 模块

### 职责

- 汇总学习档案
- 展示当前进度
- 展示练习历史、错题、考试与模板摘要

### 建议命令

- `profile --summary`
- `profile --progress`
- `profile --practice-history`
- `profile --mistakes`
- `profile --exam-history`
- `profile --templates`

## 建议的脚本模块结构

```text
scripts/
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

## 模块职责划分

### `workspace.py`

只负责：

- 用户名解析
- workspace 路径
- 目录与文件初始化

### `state.py`

只负责：

- 当前状态
- 课程进度
- 掌握度摘要

### `home.py`

只负责：

- 首页 dashboard
- resume 目标
- 推荐动作

### `learning.py`

只负责学习中心的结构能力，不负责实际讲课文案。

### `practice.py`

只负责练习中心的蓝图、记录和错题系统。

### `exam.py`

只负责考试结构、校验和报告。

### `prompt_lab.py`

只负责 Prompt Lab 流程与模板保存。

### `profile.py`

负责聚合展示，不负责底层写入。

## 推荐的用户流转

### 用户进入 skill

1. `workspace --bootstrap`
2. `home --dashboard`

### 用户继续学习

1. `home --resume`
2. `learning --lesson-meta --course <N>`

### 课程结束后进入练习

1. `practice --blueprint --course <N> --mode current`
2. 用户作答
3. `practice --record-result`
4. `learning --lesson-panel --course <N>`

### 用户进入 Prompt Lab

1. `lab --workflow --topic "<topic>"`
2. `lab --interview-blueprint --topic "<topic>"`
3. `lab --validate-slots --topic "<topic>"`
4. `lab --review-checklist --topic "<topic>"`
5. `lab --validate-draft --topic "<topic>"`

## 最终结果

当前 CLI 已稳定在平台模块模型：

- 首页负责统一导航
- 学习中心负责课程闭环
- 练习中心负责训练闭环
- 考试中心负责评估闭环
- Prompt Lab 负责实战闭环
- 学习档案负责历史与摘要视图

## 成功标准

重构后的 CLI 应满足：

- 顶层命令与产品模块一一对应
- 首页可作为统一入口
- workspace 与状态管理有独立模块承接
- 练习、考试和 Prompt Lab 的结构能力可以复用
- 后续扩展新模块时不需要继续膨胀 `__main__.py`
