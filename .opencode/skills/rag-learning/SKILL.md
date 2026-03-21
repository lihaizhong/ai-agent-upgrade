---
name: rag-learning
description: RAG（检索增强生成）系统学习与实战技能。分为学习模式和实战模式两大模块。学习模式提供 RAG 搭建的系统化课程，包括向量化、存储、检索、Embedding 模型选择、Rerank 模型选择、向量数据库选型、各种场景 RAG 搭建及企业级案例；实战模式提供真实场景题目，让用户选择 RAG 系统各组件（向量化工具、向量数据库、嵌入模型、重排模型等），然后一步步指导用户搭建、测试和调优 RAG 系统。当用户想学习 RAG 搭建、了解 RAG 知识、搭建 RAG 系统、做 RAG 练习题、选择 Embedding/Rerank 模型、选择向量数据库、或需要帮助设计 RAG 架构时，务必使用此技能。
metadata:
  version: 1.0.0
  author: iFlow CLI
  last_updated: 2026-03-22
---

# RAG 系统学习与实战

当用户触发本技能时，**按优先级使用选择方式**：

1. **优先使用 question 工具** - 交互式选择界面
2. **降级为纯文本菜单** - 直接展示文字菜单

## 使用 question 工具

```
请使用 question 工具展示功能选择：

标题：欢迎使用 RAG 系统学习与实战！
问题：请问您想做什么？
选项：
1. 学习模式 - 系统学习 RAG 搭建知识，互动问答
2. 实战模式 - 真实场景练习，逐步搭建 RAG 系统
```

## 降级为纯文本

```
欢迎使用 RAG 系统学习与实战！请选择：

1. 学习模式 - 系统学习 RAG 搭建知识，互动问答
2. 实战模式 - 真实场景练习，逐步搭建 RAG 系统

请输入「学习」或「实战」：
```

---

## 两大模式

### 1. 学习模式

用户选择「学习」后，展示课程列表让用户选择，然后展示课程内容，进行互动问答。

课程体系：
- RAG 基础概念
- 向量化（Embedding）详解
- 向量数据库选型与使用
- 检索策略与优化
- Embedding 模型选择指南
- Rerank 模型选择指南
- 场景化 RAG 搭建（文档问答、客服机器人、知识库搜索等）
- 企业级 RAG 架构设计
- RAG 性能优化与调优

详细说明：[reference/learning-mode.md](reference/learning-mode.md)
课程内容：[courses/](courses/README.md)

---

### 2. 实战模式

用户选择「实战」后，展示真实场景题目，让用户选择 RAG 系统各组件配置，然后逐步指导用户搭建、测试和调优。

实战流程：
1. 选择场景（客服机器人、文档问答、知识库搜索等）
2. 选择技术栈（Embedding 模型、向量数据库、Rerank 模型等）
3. 动手搭建（分步指导，用户自行实现）
4. 测试验证
5. 性能调优

详细说明：[reference/practice-mode.md](reference/practice-mode.md)
实战场景：[reference/scenarios.md](reference/scenarios.md)

---

常见问题：[reference/faq.md](reference/faq.md)