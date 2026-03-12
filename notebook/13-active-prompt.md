---
category: 提示优化
difficulty: 专家
type: 优化技术
year: 2023
author: Diao et al.
paper_url: https://arxiv.org/abs/2302.12246
applications: 数学推理, 逻辑推理, 代码生成, 问题选择
---

# 主动提示（Active-Prompt）

## 核心概念

主动提示（Active-Prompt）是由 Diao 等人（2023）提出的一种自适应提示方法，旨在解决传统思维链（CoT）方法依赖固定人工注释范例的问题。Active-Prompt 通过计算不确定度来选择最需要人工注释的问题，然后使用这些注释来推断每个问题。

### Active-Prompt 的定义

Active-Prompt 是一种自适应框架，能够：
- **自动选择示例**：选择最有效的示例进行注释
- **计算不确定度**：基于模型输出的不一致性计算不确定度
- **动态适应**：适应不同任务的特点
- **高效注释**：减少人工注释的工作量

### 与传统 CoT 的区别

| 特性 | 传统 CoT | Active-Prompt |
|------|---------|--------------|
| **示例选择** | 固定的人工注释 | 动态选择的示例 |
| **适应性** | 低 | 高 |
| **注释效率** | 低（需要大量注释） | 高（选择性注释） |
| **任务适应性** | 有限 | 强 |
| **不确定度考虑** | 无 | 有 |

### 工作原理

```
训练问题集
    ↓
使用少量 CoT 示例查询 LLM
    ↓
生成 k 个可能的答案
    ↓
计算不确定度（基于不一致性）
    ↓
选择最不确定的问题
    ↓
人工注释
    ↓
使用新注释范例推断每个问题
```

## Active-Prompt 的工作流程

### 步骤 1：查询 LLM

- 使用或不使用少量 CoT 示例
- 对训练问题集进行查询
- 生成多个可能的答案（k 个）

### 步骤 2：计算不确定度

- **不一致性度量**：基于 k 个答案的不一致性
- **熵计算**：计算答案分布的熵
- **方差计算**：计算答案的方差

### 步骤 3：选择问题

- 选择不确定度最高的问题
- 这些问题最需要人工注释
- 优先级排序

### 步骤 4：人工注释

- 人工注释选定的关键问题
- 添加 CoT 推理过程
- 确保注释质量

### 步骤 5：推断答案

- 使用新的注释范例
- 推断每个训练问题的答案
- 提高整体性能

## 不确定度计算方法

### 1. 不一致性度量

**原理：** 基于多个答案之间的不一致性

**方法：**
```python
def inconsistency_measure(answers):
    """
    计算答案的不一致性
    """
    # 统计答案分布
    answer_counts = {}
    for answer in answers:
        answer_counts[answer] = answer_counts.get(answer, 0) + 1
    
    # 计算不一致性
    total = len(answers)
    max_count = max(answer_counts.values())
    inconsistency = 1 - (max_count / total)
    
    return inconsistency
```

### 2. 熵计算

**原理：** 使用信息熵度量不确定性

**方法：**
```python
import numpy as np

def entropy_measure(answers):
    """
    计算答案分布的熵
    """
    # 统计答案分布
    answer_counts = {}
    for answer in answers:
        answer_counts[answer] = answer_counts.get(answer, 0) + 1
    
    # 计算概率分布
    total = len(answers)
    probabilities = [count / total for count in answer_counts.values()]
    
    # 计算熵
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    
    return entropy
```

### 3. 方差计算

**原理：** 对于数值型答案，计算方差

**方法：**
```python
import numpy as np

def variance_measure(answers):
    """
    计算数值答案的方差
    """
    # 转换为数值
    numeric_answers = [float(answer) for answer in answers]
    
    # 计算方差
    variance = np.var(numeric_answers)
    
    return variance
```

## Active-Prompt 的优势

### 1. 自适应能力

- **任务适应**：适应不同任务的特点
- **动态调整**：根据任务动态调整示例
- **优化选择**：选择最有效的示例

### 2. 注释效率

- **选择性注释**：只注释关键问题
- **减少工作量**：减少人工注释的工作量
- **提高效率**：提高注释工作的效率

### 3. 性能提升

- **更好的示例**：使用更有效的示例
- **提高准确率**：提高任务的准确率
- **泛化能力**：提高模型的泛化能力

### 4. 资源优化

- **节省资源**：节省注释资源
- **优化成本**：降低注释成本
- **时间效率**：节省时间成本

## Active-Prompt 的应用场景

### 1. 数学推理

**场景**：需要复杂数学推理的问题

**Active-Prompt 应用：**
- 选择最难的数学问题
- 人工注释推理过程
- 提高整体推理能力

### 2. 逻辑推理

**场景**：需要逻辑推理的问题

**Active-Prompt 应用：**
- 选择逻辑复杂的问题
- 注释推理步骤
- 改善逻辑推理能力

### 3. 常识推理

**场景**：需要常识推理的问题

**Active-Prompt 应用：**
- 选择需要常识的问题
- 注释推理过程
- 提高常识推理能力

### 4. 代码生成

**场景**：需要生成代码的任务

**Active-Prompt 应用：**
- 选择复杂的代码问题
- 注释生成过程
- 提高代码生成质量

## Active-Prompt 实现示例

### 基础实现框架

```python
class ActivePrompt:
    def __init__(self, llm, k_samples=5):
        self.llm = llm
        self.k_samples = k_samples  # 生成答案的数量
        self.annotated_examples = []  # 人工注释的示例
    
    def generate_answers(self, question, use_examples=True):
        """生成多个答案"""
        answers = []
        
        for _ in range(self.k_samples):
            if use_examples and self.annotated_examples:
                # 使用注释示例
                prompt = self.build_prompt_with_examples(question)
            else:
                # 不使用示例
                prompt = question
            
            answer = self.llm(prompt)
            answers.append(answer)
        
        return answers
    
    def calculate_uncertainty(self, answers):
        """计算不确定度"""
        # 使用不一致性度量
        answer_counts = {}
        for answer in answers:
            answer_counts[answer] = answer_counts.get(answer, 0) + 1
        
        total = len(answers)
        if total == 0:
            return 0
        
        max_count = max(answer_counts.values())
        uncertainty = 1 - (max_count / total)
        
        return uncertainty
    
    def select_questions(self, questions, num_select=5):
        """选择最不确定的问题"""
        uncertainties = []
        
        for question in questions:
            # 生成答案
            answers = self.generate_answers(question, use_examples=False)
            
            # 计算不确定度
            uncertainty = self.calculate_uncertainty(answers)
            
            uncertainties.append({
                'question': question,
                'uncertainty': uncertainty,
                'answers': answers
            })
        
        # 按不确定度排序
        uncertainties.sort(key=lambda x: x['uncertainty'], reverse=True)
        
        # 选择最不确定的问题
        selected = uncertainties[:num_select]
        return selected
    
    def annotate_questions(self, selected_questions):
        """人工注释问题"""
        # 这里应该是人工注释的过程
        # 返回注释后的示例
        annotated = []
        
        for item in selected_questions:
            # 在实际应用中，这里会调用人工注释接口
            # 示例：人工添加 CoT 推理
            example = {
                'question': item['question'],
                'reasoning': "[人工添加的推理过程]",
                'answer': item['answers'][0]  # 选择一个答案
            }
            annotated.append(example)
            self.annotated_examples.append(example)
        
        return annotated
    
    def infer_answers(self, questions):
        """使用注释示例推断答案"""
        results = []
        
        for question in questions:
            # 使用注释示例生成答案
            prompt = self.build_prompt_with_examples(question)
            answer = self.llm(prompt)
            
            results.append({
                'question': question,
                'answer': answer
            })
        
        return results
    
    def build_prompt_with_examples(self, question):
        """构建包含示例的提示"""
        prompt = ""
        
        # 添加注释示例
        for example in self.annotated_examples:
            prompt += f"Q: {example['question']}\n"
            prompt += f"A: {example['reasoning']}\n"
            prompt += f"答案：{example['answer']}\n\n"
        
        # 添加当前问题
        prompt += f"Q: {question}\n"
        prompt += "A: "
        
        return prompt
    
    def run(self, train_questions, test_questions):
        """运行 Active-Prompt"""
        # 选择最不确定的问题
        selected = self.select_questions(train_questions)
        
        # 人工注释
        annotated = self.annotate_questions(selected)
        
        # 使用注释示例推断测试问题的答案
        results = self.infer_answers(test_questions)
        
        return results
```

### 实际应用示例

#### 任务：数学问题求解

```python
# 初始化 Active-Prompt
llm = ChatOpenAI(model="gpt-4")
active_prompt = ActivePrompt(llm, k_samples=5)

# 训练问题
train_questions = [
    "如果 3x + 5 = 20，x 等于多少？",
    "一个三角形的底是 10，高是 5，面积是多少？",
    "如果 2x + 3y = 12 且 x = 3，y 等于多少？",
    # ... 更多训练问题
]

# 选择最不确定的问题
selected = active_prompt.select_questions(train_questions, num_select=3)

# 查看选择的问题
print("选择的问题（最不确定）：")
for item in selected:
    print(f"问题：{item['question']}")
    print(f"不确定度：{item['uncertainty']:.3f}")
    print(f"答案分布：{item['answers']}")
    print("-" * 50)

# 人工注释（在实际应用中由人工完成）
annotated = active_prompt.annotate_questions(selected)

# 测试问题
test_questions = [
    "如果 4x - 7 = 21，x 等于多少？",
    "一个圆形的半径是 5，面积是多少？",
]

# 推断答案
results = active_prompt.infer_answers(test_questions)

# 输出结果
for result in results:
    print(f"问题：{result['question']}")
    print(f"答案：{result['answer']}")
    print("-" * 50)
```

## Active-Prompt 的优化策略

### 1. 不确定度计算优化

**策略：**
- **多维度计算**：结合多种不确定度度量
- **加权组合**：根据任务特点加权
- **动态调整**：根据性能动态调整

### 2. 问题选择优化

**策略：**
- **多样性**：选择不同类型的问题
- **代表性**：选择有代表性的问题
- **难度平衡**：平衡问题难度

### 3. 注释质量优化

**策略：**
- **专家注释**：使用领域专家注释
- **质量检查**：检查注释质量
- **迭代改进**：迭代改进注释

### 4. 示例使用优化

**策略：**
- **示例排序**：按相关性排序示例
- **示例选择**：选择最相关的示例
- **示例数量**：控制示例数量

## Active-Prompt 的局限性

### 1. 依赖不确定度计算

- **挑战**：不确定度计算的准确性影响选择
- **解决方案**：使用多种不确定度度量，交叉验证

### 2. 需要人工注释

- **挑战**：仍然需要人工注释
- **解决方案**：优化注释流程，减少注释数量

### 3. 注释质量依赖

- **挑战**：注释质量影响最终性能
- **解决方案**：使用专家注释，质量检查

### 4. 计算成本

- **挑战**：需要多次查询 LLM
- **解决方案**：并行处理，缓存结果

## 最佳实践

### 1. 不确定度计算

- **多维度度量**：使用多种不确定度度量
- **交叉验证**：交叉验证不确定度计算
- **阈值设置**：合理设置选择阈值

### 2. 问题选择

- **多样性**：选择多样化的关键问题
- **代表性**：确保问题具有代表性
- **优先级**：按不确定度排序

### 3. 注释流程

- **专家参与**：邀请领域专家参与
- **质量检查**：检查注释质量
- **标准化**：标准化注释格式

### 4. 示例管理

- **版本控制**：管理示例版本
- **定期更新**：定期更新示例
- **性能监控**：监控示例性能

## Active-Prompt 与其他方法的对比

| 特性 | Active-Prompt | 传统 CoT | 少样本学习 | 自动 CoT |
|------|--------------|---------|-----------|---------|
| **示例选择** | 动态选择 | 固定 | 固定 | 自动生成 |
| **人工注释** | 选择性 | 全部 | 全部 | 无 |
| **自适应** | 强 | 弱 | 弱 | 中 |
| **不确定度** | 考虑 | 不考虑 | 不考虑 | 不考虑 |
| **注释效率** | 高 | 低 | 中 | 无需 |
| **性能** | 优秀 | 良好 | 良好 | 良好 |

## 实际应用案例

### 案例 1：数学教育

**场景**：辅助学生解决数学问题

**Active-Prompt 应用：**
- 识别学生最困难的问题类型
- 针对性注释推理过程
- 提供个性化指导

**效果：**
- 提高学生理解能力
- 减少教师工作负担
- 个性化学习体验

### 案例 2：代码调试

**场景**：帮助开发者调试代码

**Active-Prompt 应用：**
- 选择最难调试的代码问题
- 注释调试推理过程
- 提供调试建议

**效果：**
- 提高调试效率
- 减少调试时间
- 改善代码质量

### 案例 3：科学研究

**场景**：辅助科学研究发现

**Active-Prompt 应用：**
- 识别最复杂的科学问题
- 注释研究推理过程
- 提供研究建议

**效果：**
- 加速研究进程
- 提高研究质量
- 促进科学发现

## 评估指标

### 1. 选择质量

- **不确定性相关性**：不确定度与实际难度的相关性
- **覆盖率**：覆盖关键问题的程度
- **多样性**：选择问题的多样性

### 2. 注释效率

- **注释数量**：需要注释的问题数量
- **注释时间**：注释所需时间
- **注释质量**：注释的质量评分

### 3. 性能提升

- **准确率提升**：与基线相比的准确率提升
- **泛化能力**：在新任务上的表现
- **鲁棒性**：对扰动的鲁棒性

## 相关技术

- **思维链提示（Chain-of-Thought）**：基础技术
- **少样本学习（Few-Shot Learning）**：基础方法
- **自动 CoT（Auto-CoT）**：自动生成 CoT
- **主动学习（Active Learning）**：学习理论
- **不确定性估计（Uncertainty Estimation）**：统计方法

## 参考资料

- Diao et al. (2023): "Active Prompting with Chain-of-Thought for Large Language Models"
- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/activeprompt

## 练习

1. 实现一个简单的 Active-Prompt 框架
2. 实现多种不确定度计算方法
3. 使用 Active-Prompt 优化数学问题的求解
4. 对比 Active-Prompt 和传统 CoT 的性能
5. 实现 Active-Prompt 的自动化注释流程