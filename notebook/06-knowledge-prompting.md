---
category: 知识技术
difficulty: 中级
type: 知识技术
year: 2022
author: Liu et al.
paper_url: https://arxiv.org/abs/2110.07407
applications: 事实验证, 知识问答, 决策支持, 数据分析
---

# 链式提示 (Prompt Chaining)

## 核心概念

链式提示（Prompt Chaining）是一种将复杂任务分解为多个子任务的提示工程技术。通过创建一系列提示操作，每个提示处理一个子任务，前一个提示的输出作为后一个提示的输入，最终完成整体任务。

## 工作原理

### 为什么需要链式提示

大语言模型在处理复杂任务时，仅使用一个非常详细的提示可能无法完成任务。链式提示通过以下方式改善这种情况：

1. **任务分解** - 将复杂任务拆分为可管理的子任务
2. **逐步处理** - 每个子任务独立处理，降低复杂度
3. **结果转换** - 对中间结果进行转换或处理
4. **逐步优化** - 每个步骤都可以独立优化

### 工作流程

```
原始复杂任务
    ↓
分解为子任务
    ↓
提示 1 → 子任务 1 → 输出 1
    ↓
提示 2（输入 1）→ 子任务 2 → 输出 2
    ↓
提示 3（输入 2）→ 子任务 3 → 输出 3
    ↓
...
    ↓
最终输出
```

## 优势

### 1. 提高性能
- 每个子任务更专注
- 减少单次任务的复杂度
- 提高整体准确性

### 2. 增强透明度
- 可以看到每个步骤的输出
- 便于理解和调试
- 提高可解释性

### 3. 增加控制性
- 可以单独控制每个步骤
- 便于调整和优化
- 提高灵活性

### 4. 提高可靠性
- 减少错误传播
- 可以验证中间结果
- 更容易定位问题

### 5. 改善可维护性
- 模块化设计
- 易于更新和修改
- 便于复用

## 应用场景

链式提示适用于：

- ✅ **复杂文档处理** - 大型文档问答、摘要、提取
- ✅ **多步骤任务** - 需要多个转换或操作的任务
- ✅ **对话系统** - 构建多轮对话助手
- ✅ **个性化体验** - 根据用户行为调整响应
- ✅ **数据处理流程** - 多阶段的数据转换
- ✅ **复杂推理** - 需要多步推理的任务

## 详细示例：文档问答

### 场景描述

根据大型文本文档回答问题。由于文档较长，直接问答可能效果不佳，因此采用链式提示方法。

### 任务分解

1. **步骤 1**：从文档中提取与问题相关的引文
2. **步骤 2**：基于提取的引文和原始文档生成答案

### 步骤 1：提取相关引文

**提示 1：**

```
你是一个很有帮助的助手。你的任务是根据文档回答问题。
第一步是从文档中提取与问题相关的引文，由####分隔。
请使用<quotes></quotes>输出引文列表。
如果没有找到相关引文，请回应"未找到相关引文！"。
####
{{文档}}
####
```

**用户问题（通过 user 角色传递）：**
```
文档中提到了哪些提示技术？
```

**输出 1：**

```
<quotes>
- Chain-of-thought (CoT) prompting[27]
- Generated knowledge prompting[37]
- Least-to-most prompting[38]
- Self-consistency decoding[39]
- Complexity-based prompting[41]
- Self-refine[42]
- Tree-of-thought prompting[43]
- Maieutic prompting[45]
- Directional-stimulus prompting[46]
- Textual inversion and embeddings[59]
- Using gradient descent to search for prompts[61][62][63][64]
- Prompt injection[65][66][67]
</quotes>
```

### 步骤 2：生成答案

**提示 2：**

```
根据从文档中提取的相关引文（由<quotes></quotes>分隔）和原始文档（由####分隔），
请构建对问题的回答。请确保答案准确、语气友好且有帮助。
####
{{文档}}
####
<quotes>
- Chain-of-thought (CoT) prompting[27]
- Generated knowledge prompting[37]
- Least-to-most prompting[38]
- Self-consistency decoding[39]
- Complexity-based prompting[41]
- Self-refine[42]
- Tree-of-thought prompting[43]
- Maieutic prompting[45]
- Directional-stimulus prompting[46]
- Textual inversion and embeddings[59]
- Using gradient descent to search for prompts[61][62][63][64]
- Prompt injection[65][66][67]
</quotes>
```

**输出 2：**

```
文档中提到的提示技术包括：
1. Chain-of-thought (CoT) prompting[27]
2. Generated knowledge prompting[37]
3. Least-to-most prompting[38]
4. Self-consistency decoding[39]
5. Complexity-based prompting[41]
6. Self-refine[42]
7. Tree-of-thought prompting[43]
8. Maieutic prompting[45]
9. Directional-stimulus prompting[46]
10. Textual inversion and embeddings[59]
11. Using gradient descent to search for prompts[61][62][63][64]
12. Prompt injection[65][66][67]

每一种技术都采用独特的策略来增强或明确与大型语言模型的互动，
以产生期望的结果。
```

### 扩展：清理引用标志

可以添加第三个提示来移除引用标志（如 `[27]`）：

**提示 3：**

```
请移除以下答案中的引用标志（如 [27]），保持内容的其他部分不变：
####
{{输出 2}}
####
```

**输出 3：**

```
文档中提到的提示技术包括：
1. Chain-of-thought (CoT) prompting
2. Generated knowledge prompting
3. Least-to-most prompting
4. Self-consistency decoding
5. Complexity-based prompting
6. Self-refine
7. Tree-of-thought prompting
8. Maieutic prompting
9. Directional-stimulus prompting
10. Textual inversion and embeddings
11. Using gradient descent to search for prompts
12. Prompt injection

每一种技术都采用独特的策略来增强或明确与大型语言模型的互动，
以产生期望的结果。
```

## 设计链式提示的策略

### 1. 任务分解

**原则：**
- 将复杂任务分解为逻辑独立的子任务
- 每个子任务应该有明确的输入和输出
- 子任务之间应该有清晰的依赖关系

**示例：**
```
任务：分析一篇学术论文
分解：
1. 提取摘要
2. 提取关键发现
3. 评估方法论
4. 总结贡献
```

### 2. 提示设计

**每个提示应该：**
- 有明确的目标
- 清晰定义输入格式
- 明确指定输出格式
- 包含必要的上下文

**模板：**
```
你是一个[角色]。你的任务是[任务描述]。
输入格式：[输入格式描述]
输出格式：[输出格式描述]
####
{{输入内容}}
####
```

### 3. 输出转换

**可能需要的转换：**
- 格式化（JSON、XML 等）
- 清理（移除无关内容）
- 提取（提取关键信息）
- 聚合（合并多个输出）

### 4. 错误处理

**考虑以下情况：**
- 某个步骤失败
- 输出格式不正确
- 输出内容为空
- 输出质量不达标

**处理策略：**
- 添加验证步骤
- 提供回退机制
- 记录错误信息
- 尝试重试

## 实现模式

### 模式 1：线性链

```
输入 → 提示 1 → 输出 1 → 提示 2 → 输出 2 → ... → 最终输出
```

**适用：** 顺序依赖的任务

### 模式 2：分支链

```
输入 → 提示 1 → 输出 1
          ├→ 提示 2a → 输出 2a
          └→ 提示 2b → 输出 2b
```

**适用：** 需要并行处理的任务

### 模式 3：循环链

```
输入 → 提示 1 → 输出 1
          ↓
         提示 2 → 输出 2
          ↓
         提示 3 → 输出 3
          ↓
         [判断] → 是 → 继续循环
                 → 否 → 最终输出
```

**适用：** 需要迭代优化的任务

### 模式 4：并行聚合链

```
输入 → ├→ 提示 1 → 输出 1 ─┐
       ├→ 提示 2 → 输出 2 ─┼→ 聚合 → 最终输出
       └→ 提示 3 → 输出 3 ─┘
```

**适用：** 需要多个角度分析的任务

## 最佳实践

### 1. 明确步骤定义

- 为每个步骤定义清晰的名称
- 说明每个步骤的目的
- 记录输入输出格式

### 2. 模块化设计

- 每个提示应该是独立的模块
- 可以单独测试和优化
- 便于复用和维护

### 3. 错误处理

- 验证每个步骤的输出
- 提供错误恢复机制
- 记录日志便于调试

### 4. 性能优化

- 考虑并行执行不依赖的步骤
- 缓存中间结果
- 优化提示长度

### 5. 文档化

- 记录整个链的设计
- 说明每个步骤的意图
- 提供使用示例

## 常见应用场景

### 1. 文档处理

```
输入文档
  ↓
提取关键信息 → 结构化数据
  ↓
生成摘要 → 摘要文本
  ↓
翻译 → 多语言摘要
```

### 2. 代码分析

```
输入代码
  ↓
提取函数 → 函数列表
  ↓
分析依赖 → 依赖图
  ↓
生成文档 → API 文档
```

### 3. 数据处理

```
输入数据
  ↓
数据清洗 → 清洁数据
  ↓
特征提取 → 特征向量
  ↓
模型预测 → 预测结果
```

### 4. 对话系统

```
用户输入
  ↓
意图识别 → 意图类别
  ↓
实体提取 → 实体列表
  ↓
查询生成 → 查询语句
  ↓
结果生成 → 响应文本
```

## 与其他技术的结合

### 1. 链式提示 + 思维链

```
输入问题
  ↓
思维链提示 → 推理过程
  ↓
答案提取 → 最终答案
  ↓
答案验证 → 验证结果
```

### 2. 链式提示 + 自我一致性

```
输入问题
  ↓
生成多个推理路径 → 路径 1, 2, 3...
  ↓
答案聚合 → 多数投票
  ↓
结果验证 → 最终答案
```

### 3. 链式提示 + RAG

```
用户问题
  ↓
检索相关文档 → 文档列表
  ↓
提取关键信息 → 信息摘要
  ↓
生成答案 → 最终答案
```

## 局限性

### 1. 延迟增加
- 多个步骤串行执行
- 总耗时增加
- 可能影响用户体验

### 2. 成本增加
- 每个 API 调用都有成本
- 步骤越多成本越高
- 需要权衡成本和性能

### 3. 复杂性增加
- 设计和调试更复杂
- 需要更多维护工作
- 可能引入新的错误

### 4. 错误累积
- 前面的错误影响后续
- 需要良好的错误处理
- 可能需要回退机制

## 实现建议

### 基础实现

```python
class PromptChain:
    def __init__(self):
        self.steps = []
    
    def add_step(self, prompt_template, name=None):
        """添加一个步骤到链中"""
        step = {
            'template': prompt_template,
            'name': name or f"step_{len(self.steps)+1}"
        }
        self.steps.append(step)
        return self
    
    def execute(self, initial_input):
        """执行整个链"""
        current_output = initial_input
        results = {}
        
        for step in self.steps:
            # 格式化提示
            prompt = step['template'].format(input=current_output)
            
            # 调用模型
            response = call_llm(prompt)
            
            # 保存结果
            results[step['name']] = response
            
            # 更新当前输出
            current_output = response
        
        return current_output, results
```

### 高级实现

```python
class AdvancedPromptChain:
    def __init__(self):
        self.steps = []
        self.validators = {}
        self.retry_policy = {}
    
    def add_step(self, template, name, validator=None, max_retries=3):
        """添加步骤，包含验证和重试策略"""
        step = {
            'template': template,
            'name': name
        }
        self.steps.append(step)
        if validator:
            self.validators[name] = validator
        if max_retries > 0:
            self.retry_policy[name] = max_retries
        return self
    
    def execute(self, initial_input):
        """执行链，包含错误处理"""
        context = {'input': initial_input}
        results = {}
        
        for step in self.steps:
            name = step['name']
            max_retries = self.retry_policy.get(name, 0)
            
            for attempt in range(max_retries + 1):
                try:
                    # 执行步骤
                    prompt = step['template'].format(**context)
                    response = call_llm(prompt)
                    
                    # 验证输出
                    if name in self.validators:
                        if not self.validators[name](response):
                            raise ValueError("Validation failed")
                    
                    # 保存结果
                    results[name] = response
                    context[name] = response
                    break
                    
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    continue
        
        return context.get(f"step_{len(self.steps)}"), results
```

## 评估指标

### 1. 性能指标
- **准确率**：最终输出的准确性
- **延迟**：总执行时间
- **成本**：API 调用总成本
- **成功率**：任务完成的成功率

### 2. 质量指标
- **一致性**：多次执行的稳定性
- **鲁棒性**：对异常输入的处理能力
- **可解释性**：中间输出的可理解性

### 3. 可维护性指标
- **模块化程度**：步骤的独立性
- **可复用性**：步骤的可复用程度
- **文档完整性**：设计和实现的文档化程度

## 相关技术

- **思维链提示（Chain-of-Thought）**：展示推理过程
- **自我一致性（Self-Consistency）**：多次采样投票
- **生成知识提示（Generated Knowledge）**：生成背景知识
- **检索增强生成（RAG）**：结合外部知识库
- **Least-to-Most Prompting**：从简单到复杂分解

## 参考资料

- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/prompt_chaining
- Anthropic Prompt Engineering Guide: https://docs.anthropic.com/claude/docs/prompt-engineering

## 练习

1. 设计一个链式提示系统来分析一篇学术论文
2. 实现一个文档摘要系统，使用链式提示提取关键信息并生成摘要
3. 创建一个代码审查系统，使用链式提示进行多步骤分析
4. 实现一个带错误处理的链式提示框架
5. 对比链式提示和单步提示在复杂任务上的性能差异