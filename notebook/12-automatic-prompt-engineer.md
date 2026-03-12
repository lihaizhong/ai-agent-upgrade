---
category: 提示优化
difficulty: 专家
type: 优化技术
year: 2022
author: Zhou et al.
paper_url: https://arxiv.org/abs/2211.01910
applications: 提示优化, 任务迁移, 零样本学习, 自动提示
---

# 自动提示工程师（Automatic Prompt Engineer, APE）

## 核心概念

自动提示工程师（Automatic Prompt Engineer，简称 APE）是由 Zhou 等人（2022）提出的一个用于自动指令生成和选择的框架。APE 将指令生成问题构建为自然语言合成问题，使用 LLMs 作为黑盒优化问题的解决方案来生成和搜索候选解。

### APE 的定义

APE 是一个自动化框架，能够：
- **自动生成指令**：无需人工设计，自动生成任务指令
- **指令选择**：从多个候选项中选择最优指令
- **自然语言合成**：将指令生成视为自然语言合成问题
- **黑盒优化**：将 LLM 作为黑盒优化器

### 工作原理

```
输出演示（Output Demonstrations）
    ↓
大型语言模型（推理模型）
    ↓
生成指令候选项（Candidate Instructions）
    ↓
目标模型执行指令
    ↓
计算评估分数
    ↓
选择最优指令
```

## APE 框架架构

### 核心组件

```
┌─────────────────┐
│  输出演示       │
│  (Output)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  推理模型       │
│  (LLM Inference) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  指令候选项     │
│  (Candidates)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  目标模型       │
│  (Target Model) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  评估系统       │
│  (Evaluation)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  最优指令       │
│  (Best Prompt)  │
└─────────────────┘
```

### 工作流程

#### 步骤 1：准备输出演示

- 收集任务的输入输出对
- 提供期望的输出示例
- 构建演示数据集

#### 步骤 2：生成指令候选项

- 使用大型语言模型作为推理模型
- 基于输出演示生成指令候选项
- 生成多个不同的指令变体

#### 步骤 3：执行指令

- 使用目标模型执行每个指令候选项
- 在测试集上评估指令效果
- 收集执行结果

#### 步骤 4：评估和选择

- 计算每个指令的评估分数
- 根据分数排序指令候选项
- 选择表现最优的指令

## APE 的优势

### 1. 自动化

- **无需人工设计**：自动生成指令，减少人工工作
- **快速迭代**：可以快速生成和测试多个指令
- **规模化**：可以处理大量任务

### 2. 优化能力

- **黑盒优化**：将 LLM 作为优化器，不需要了解内部机制
- **搜索能力**：能够在指令空间中搜索最优解
- **自适应**：可以根据任务特点调整指令

### 3. 客观评估

- **量化评估**：基于评估分数客观比较指令
- **数据驱动**：基于实际表现选择指令
- **可重复**：评估过程可重复和验证

### 4. 发现新指令

- **超越人类直觉**：可能发现人类想不到的指令
- **创新性**：能够生成新颖的指令形式
- **优化空间**：探索更大的指令空间

## 应用案例：零样本 CoT 提示优化

### 背景

Kojima 等人（2022）提出了"让我们一步一步地思考"的零样本 CoT 提示，但 APE 发现了更好的提示。

### APE 发现的提示

**提示：**
```
让我们一步一步地解决这个问题，以确保我们有正确的答案。
```

### 性能对比

APE 发现的提示在以下基准测试中表现优异：

| 基准测试 | Kojima 提示 | APE 提示 | 提升 |
|---------|------------|---------|------|
| **MultiArith** | 基线 | 更高 | 显著提升 |
| **GSM8K** | 基线 | 更高 | 显著提升 |

### 分析

APE 发现的提示相比原始提示：
- **更具体**：明确说明"确保有正确的答案"
- **更完整**：完整描述了解决问题的过程
- **更有效**：引发了更好的思维链推理

## APE 实现示例

### 基础实现框架

```python
class APE:
    def __init__(self, inference_model, target_model, evaluator):
        self.inference_model = inference_model  # 推理模型
        self.target_model = target_model        # 目标模型
        self.evaluator = evaluator              # 评估器
    
    def generate_candidates(self, output_demonstrations, num_candidates=10):
        """生成指令候选项"""
        prompt = f"""
        基于以下输出演示，生成 {num_candidates} 个不同的任务指令：
        
        输出示例：
        {output_demonstrations}
        
        指令候选项：
        """
        
        candidates = self.inference_model(prompt)
        # 解析生成的指令
        instructions = self.parse_instructions(candidates)
        return instructions
    
    def evaluate_instructions(self, instructions, test_set):
        """评估指令"""
        results = []
        
        for instruction in instructions:
            # 使用目标模型执行指令
            prompt = f"{instruction}\n\n"
            scores = []
            
            for test_input, expected_output in test_set:
                full_prompt = prompt + test_input
                actual_output = self.target_model(full_prompt)
                
                # 计算评估分数
                score = self.evaluator.evaluate(
                    expected_output, 
                    actual_output
                )
                scores.append(score)
            
            # 计算平均分数
            avg_score = sum(scores) / len(scores)
            results.append({
                'instruction': instruction,
                'score': avg_score,
                'scores': scores
            })
        
        return results
    
    def select_best_instruction(self, results):
        """选择最优指令"""
        # 按分数排序
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        return sorted_results[0]
    
    def run(self, output_demonstrations, test_set, num_candidates=10):
        """运行 APE"""
        # 生成候选项
        instructions = self.generate_candidates(
            output_demonstrations, 
            num_candidates
        )
        
        # 评估指令
        results = self.evaluate_instructions(instructions, test_set)
        
        # 选择最优指令
        best_instruction = self.select_best_instruction(results)
        
        return best_instruction, results
```

### 实际应用示例

#### 任务：数学问题求解

```python
# 初始化 APE
inference_model = ChatOpenAI(model="gpt-4")
target_model = ChatOpenAI(model="gpt-3.5-turbo")
evaluator = MathEvaluator()

ape = APE(inference_model, target_model, evaluator)

# 准备数据
output_demonstrations = """
输入：2 + 2 = ?
输出：4

输入：5 × 3 = ?
输出：15

输入：10 - 4 = ?
输出：6
"""

test_set = [
    ("3 + 4 = ?", "7"),
    ("8 × 2 = ?", "16"),
    ("15 - 7 = ?", "8"),
]

# 运行 APE
best_instruction, all_results = ape.run(
    output_demonstrations, 
    test_set,
    num_candidates=10
)

print("最优指令：")
print(best_instruction['instruction'])
print(f"平均分数：{best_instruction['score']}")
```

#### 可能生成的指令候选项

```
1. "计算以下数学表达式的结果。"
2. "请解决这个数学问题。"
3. "让我们一步一步地解决这个问题，以确保我们有正确的答案。"
4. "请给出这个数学问题的答案。"
5. "仔细计算以下表达式的值。"
6. "逐步解决这个数学问题。"
7. "请准确地计算这个表达式。"
8. "解决这个数学运算。"
9. "请提供这个数学问题的正确答案。"
10. "计算并给出最终结果。"
```

## APE 的评估方法

### 1. 准确率评估

**适用：** 有明确正确答案的任务

**方法：**
```python
def accuracy_evaluator(expected, actual):
    return 1 if expected.strip() == actual.strip() else 0
```

### 2. 相似度评估

**适用：** 开放性任务

**方法：**
```python
from sentence_transformers import SentenceTransformer

def similarity_evaluator(expected, actual):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    emb1 = model.encode(expected)
    emb2 = model.encode(actual)
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([emb1], [emb2])[0][0]
```

### 3. 人工评估

**适用：** 需要人工判断的任务

**方法：**
- 邀请领域专家评估
- 使用评估量表（1-5 分）
- 综合多位专家的意见

## APE 的优化策略

### 1. 候选项生成优化

**策略：**
- **多样性**：生成多样化的指令候选项
- **数量控制**：平衡数量和质量
- **过滤**：过滤明显不合理的指令

### 2. 评估优化

**策略：**
- **多维度评估**：从多个维度评估指令
- **加权评分**：根据重要性加权
- **统计显著性**：确保结果可靠

### 3. 搜索策略优化

**策略：**
- **迭代搜索**：基于结果迭代优化
- **启发式搜索**：使用启发式方法
- **并行搜索**：并行生成和评估

### 4. 数据优化

**策略：**
- **高质量演示**：使用高质量的输出演示
- **多样化测试集**：使用多样化的测试集
- **平衡数据**：确保测试集的平衡性

## APE 的变体和扩展

### 1. Prompt-OIRL

**特点：**
- 使用离线逆强化学习
- 生成与查询相关的提示
- 考虑用户偏好

**应用：** 个性化提示生成

### 2. OPRO (Optimization by PROmpting)

**特点：**
- 让 LLMs 优化提示
- 发现"深呼吸"技巧
- 提高数学问题表现

**应用：** 提示优化

### 3. AutoPrompt

**特点：**
- 基于梯度引导搜索
- 自动创建各种任务的提示
- 使用可训练的触发器

**应用：** 自动提示生成

### 4. Prefix Tuning

**特点：**
- 轻量级 fine-tuning 替代方案
- 添加可训练的连续前缀
- 适用于 NLG 任务

**应用：** 模型优化

### 5. Prompt Tuning

**特点：**
- 通过反向传播学习软提示
- 避免更新模型参数
- 提高任务性能

**应用：** 模型适配

## APE 的应用场景

### 1. 零样本学习

**场景：** 在没有示例的情况下完成新任务

**APE 能力：**
- 自动生成任务指令
- 优化指令表述
- 提高任务性能

### 2. 少样本学习

**场景：** 使用少量示例完成任务

**APE 能力：**
- 优化示例展示方式
- 改进指令设计
- 提高学习效率

### 3. 提示优化

**场景：** 优化现有提示的性能

**APE 能力：**
- 生成提示变体
- 评估提示效果
- 选择最优提示

### 4. 任务迁移

**场景：** 将任务迁移到新领域

**APE 能力：**
- 适应新领域特点
- 生成领域特定指令
- 保持任务性能

## APE 的局限性

### 1. 依赖输出演示

- **挑战**：输出演示的质量影响生成结果
- **解决方案**：使用高质量、多样化的演示

### 2. 计算成本高

- **挑战**：需要生成和评估多个候选项
- **解决方案**：优化搜索策略，并行处理

### 3. 评估标准依赖

- **挑战**：评估标准的选择影响结果
- **解决方案**：使用多维评估，人工验证

### 4. 上下文限制

- **挑战**：指令长度受模型上下文限制
- **解决方案**：压缩指令，分批处理

## 最佳实践

### 1. 数据准备

- **高质量演示**：使用准确、清晰的输出演示
- **多样化测试集**：覆盖任务的不同方面
- **平衡数据**：确保各类别平衡

### 2. 候选项生成

- **多样性**：生成多样化的指令
- **合理数量**：10-20 个候选项通常足够
- **过滤机制**：过滤明显不合理的指令

### 3. 评估设计

- **多维评估**：从多个维度评估
- **加权评分**：根据重要性加权
- **人工验证**：关键任务需要人工验证

### 4. 结果验证

- **交叉验证**：使用多个测试集验证
- **统计分析**：进行统计分析
- **持续监控**：监控指令在实际应用中的表现

## APE 与其他方法的对比

| 特性 | APE | 手工设计 | AutoPrompt | Prompt Tuning |
|------|-----|---------|-----------|---------------|
| **自动化程度** | 高 | 低 | 高 | 中 |
| **计算成本** | 中 | 低 | 高 | 高 |
| **需要训练** | 否 | 否 | 是 | 是 |
| **通用性** | 高 | 低 | 中 | 中 |
| **可解释性** | 高 | 高 | 中 | 低 |
| **优化能力** | 强 | 弱 | 强 | 中 |

## 实际应用案例

### 案例 1：代码生成

**场景：** 优化代码生成的提示

**APE 实现：**
1. 收集代码输入输出对
2. 生成代码生成指令候选项
3. 评估指令在代码生成任务上的表现
4. 选择最优指令

**效果：**
- 提高代码生成质量
- 减少语法错误
- 提高代码可读性

### 案例 2：文本分类

**场景：** 优化文本分类的提示

**APE 实现：**
1. 收集文本分类示例
2. 生成分类指令候选项
3. 评估指令在分类任务上的准确率
4. 选择最优指令

**效果：**
- 提高分类准确率
- 减少误分类
- 改善类别平衡

### 案例 3：问答系统

**场景：** 优化问答系统的提示

**APE 实现：**
1. 收集问答对
2. 生成问答指令候选项
3. 评估指令在问答任务上的表现
4. 选择最优指令

**效果：**
- 提高答案准确性
- 改善答案相关性
- 增强可解释性

## 评估指标

### 1. 任务性能

- **准确率**：任务的准确率
- **F1 分数**：综合性能指标
- **召回率**：信息召回能力

### 2. 指令质量

- **清晰度**：指令的清晰程度
- **完整性**：指令的完整程度
- **有效性**：指令的有效性

### 3. 系统性能

- **生成时间**：指令生成时间
- **评估时间**：指令评估时间
- **总成本**：总体计算成本

## 相关技术

- **自动 CoT（Auto-CoT）**：自动生成思维链
- **提示优化（Prompt Optimization）**：优化现有提示
- **元学习（Meta-Learning）**：学习如何学习
- **神经架构搜索（NAS）**：搜索最优架构
- **强化学习（RL）**：通过反馈优化

## 参考资料

- Zhou et al. (2022): "Large Language Models Are Human-Level Prompt Engineers"
- Kojima et al. (2022): "Large Language Models are Zero-Shot Reasoners"
- Prompt-OIRL: "Prompt Engineering with Offline Inverse Reinforcement Learning"
- OPRO: "Large Language Models as Optimizers"
- AutoPrompt: "Autoregressive Prompt Engineering for Large Language Models"
- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/ape

## 练习

1. 实现一个简单的 APE 框架
2. 使用 APE 优化一个数学问题的提示
3. 对比 APE 生成的指令和手工设计的指令
4. 实现多维评估系统
5. 将 APE 应用于实际任务（如代码生成、文本分类）