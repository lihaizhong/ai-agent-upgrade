---
category: 提示优化
difficulty: 专家
type: 优化技术
year: 2023
author: Li et al.
paper_url: https://arxiv.org/abs/2302.11520
applications: 文本摘要, 问答系统, 代码生成, 对话系统
---

# 方向性刺激提示（Directional Stimulus Prompting, DSP）

## 核心概念

方向性刺激提示（Directional Stimulus Prompting，简称 DSP）是由 Li 等人（2023）提出的一种新型提示技术，旨在更好地指导 LLM 生成所需的输出。

### DSP 的定义

DSP 是一个通过小型策略模型生成方向性刺激，并可结合监督学习或强化学习进行优化的提示框架：
- **策略 LM**：训练一个可调节的策略语言模型来生成刺激/提示
- **黑盒 LLM**：使用冻结的、强大的 LLM 来生成最终输出
- **训练方式灵活**：可通过监督微调或 RL 优化该策略 LM
- **方向性引导**：通过方向性刺激引导黑盒 LLM 生成期望的输出

### 核心思想

DSP 的核心思想是将提示生成过程形式化：
- **分离关注点**：将提示生成和答案生成分离
- **优化提示**：专门优化提示生成过程
- **黑盒利用**：利用强大的黑盒 LLM 的能力
- **方向性控制**：通过方向性刺激控制输出方向

### 与标准提示的对比

| 特性 | 标准提示 | DSP |
|------|---------|-----|
| **提示生成** | 人工设计 | 策略 LM 生成 |
| **优化方法** | 手工调整 | 监督学习或 RL 优化 |
| **提示质量** | 依赖经验 | 系统优化 |
| **适应性** | 低 | 高 |
| **可扩展性** | 有限 | 强 |

## DSP 的工作原理

### 架构概览

```
策略 LM（小模型）
    ↓
生成方向性刺激/提示
    ↓
黑盒 LLM（大模型）
    ↓
生成输出
    ↓
评估反馈
    ↓
监督学习或 RL 优化策略 LM
    ↓
迭代改进
```

### 核心组件

#### 1. 策略 LM（Policy LM）

- **作用**：生成方向性刺激/提示
- **特点**：可以是较小的模型
- **优化**：可通过监督学习或 RL 进行优化
- **目标**：生成能引导黑盒 LLM 产生期望输出的提示

#### 2. 黑盒 LLM（Black-Box LLM）

- **作用**：生成最终输出
- **特点**：冻结的、强大的模型
- **输入**：策略 LM 生成的提示 + 原始输入
- **输出**：期望的输出

#### 3. 评估器（Evaluator）

- **作用**：评估输出质量
- **指标**：根据任务定义评估指标
- **反馈**：提供反馈给策略 LM
- **优化**：为监督学习或 RL 提供优化信号

#### 4. 优化机制

- **作用**：优化策略 LM
- **方法**：可使用监督微调，或在需要时使用 RL 算法（如 PPO、REINFORCE）
- **监督信号**：可来自成对输入输出或高质量刺激示例
- **目标**：生成更能引导黑盒 LLM 完成任务的方向性刺激

### 工作流程

#### 步骤 1：初始化

- 初始化策略 LM
- 准备黑盒 LLM（冻结）
- 定义评估指标
- 设置训练超参数

#### 步骤 2：训练循环

```python
for episode in range(num_episodes):
    # 1. 采样输入
    input_sample = sample_input(training_data)
    
    # 2. 策略 LM 生成提示
    stimulus = policy_lm.generate(input_sample)
    
    # 3. 黑盒 LLM 生成输出
    prompt = combine_stimulus(stimulus, input_sample)
    output = black_box_llm.generate(prompt)
    
    # 4. 评估输出
    reward = evaluator.evaluate(output, ground_truth)
    
    # 5. 更新策略 LM
    policy_lm.update(reward)
```

#### 步骤 3：推理

```python
# 使用训练好的策略 LM
input_sample = "用户输入"

# 策略 LM 生成方向性刺激
stimulus = policy_lm.generate(input_sample)

# 组合提示
prompt = f"{stimulus}\n\n{input_sample}"

# 黑盒 LLM 生成输出
output = black_box_llm.generate(prompt)
```

## DSP 的优势

### 1. 提示优化

- **系统化**：系统化地优化提示
- **自动化**：自动化提示生成过程
- **数据驱动**：基于数据驱动优化

### 2. 效率提升

- **小策略 LM**：策略 LM 可以很小
- **快速优化**：优化过程快速
- **资源高效**：资源使用高效

### 3. 适应性

- **任务适应**：适应不同任务
- **动态调整**：动态调整策略
- **持续改进**：持续改进性能

### 4. 可扩展性

- **模型无关**：可以用于任何黑盒 LLM
- **任务通用**：适用于各种任务
- **易于扩展**：易于扩展到新任务

## DSP 的应用场景

### 1. 文本摘要

**场景**：生成高质量的文本摘要

**DSP 应用：**
- 策略 LM 生成摘要方向提示
- 引导 LLM 生成特定风格的摘要
- 优化摘要的准确性和流畅性

### 2. 问答系统

**场景**：回答复杂问题

**DSP 应用：**
- 策略 LM 生成推理方向提示
- 引导 LLM 进行正确推理
- 提高答案的准确性

### 3. 代码生成

**场景**：生成符合要求的代码

**DSP 应用：**
- 策略 LM 生成代码风格提示
- 引导 LLM 生成特定风格的代码
- 提高代码质量

### 4. 对话系统

**场景**：生成符合人设的对话

**DSP 应用：**
- 策略 LM 生成人设提示
- 引导 LLM 保持人设一致性
- 提高对话质量

## DSP 的实现

### 基础实现框架

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Tuple

class DirectionalStimulusPrompting:
    def __init__(
        self,
        policy_model_name: str,
        blackbox_model_name: str,
        evaluator,
        rl_optimizer
    ):
        # 初始化策略 LM
        self.policy_tokenizer = AutoTokenizer.from_pretrained(policy_model_name)
        self.policy_model = AutoModelForCausalLM.from_pretrained(policy_model_name)
        
        # 初始化黑盒 LLM（冻结）
        self.blackbox_tokenizer = AutoTokenizer.from_pretrained(blackbox_model_name)
        self.blackbox_model = AutoModelForCausalLM.from_pretrained(blackbox_model_name)
        for param in self.blackbox_model.parameters():
            param.requires_grad = False
        
        # 评估器和优化器
        self.evaluator = evaluator
        self.rl_optimizer = rl_optimizer
    
    def generate_stimulus(
        self,
        input_text: str,
        max_length: int = 100
    ) -> str:
        """生成方向性刺激"""
        inputs = self.policy_tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.policy_model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
        
        stimulus = self.policy_tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        return stimulus
    
    def generate_output(
        self,
        input_text: str,
        stimulus: str,
        max_length: int = 512
    ) -> str:
        """使用黑盒 LLM 生成输出"""
        # 组合提示
        prompt = f"{stimulus}\n\n{input_text}"
        
        inputs = self.blackbox_tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )
        
        with torch.no_grad():
            outputs = self.blackbox_model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True
            )
        
        output = self.blackbox_tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        return output
    
    def train(
        self,
        training_data: List[Dict],
        num_episodes: int = 1000,
        batch_size: int = 8
    ):
        """训练策略 LM"""
        for episode in range(num_episodes):
            # 采样批次
            batch = self.sample_batch(training_data, batch_size)
            
            episode_rewards = []
            
            for sample in batch:
                # 生成刺激
                stimulus = self.generate_stimulus(sample['input'])
                
                # 生成输出
                output = self.generate_output(sample['input'], stimulus)
                
                # 评估
                reward = self.evaluator.evaluate(
                    output,
                    sample['ground_truth']
                )
                
                episode_rewards.append(reward)
            
            # 更新策略 LM
            self.rl_optimizer.update(episode_rewards)
            
            # 打印进度
            if episode % 100 == 0:
                avg_reward = sum(episode_rewards) / len(episode_rewards)
                print(f"Episode {episode}, Avg Reward: {avg_reward:.4f}")
    
    def sample_batch(
        self,
        data: List[Dict],
        batch_size: int
    ) -> List[Dict]:
        """采样批次"""
        import random
        return random.sample(data, min(batch_size, len(data)))
```

### 评估器实现

```python
class SummarizationEvaluator:
    """摘要任务评估器"""
    
    def __init__(self, metric: str = "rouge"):
        self.metric = metric
    
    def evaluate(
        self,
        generated: str,
        reference: str
    ) -> float:
        """评估生成的摘要"""
        if self.metric == "rouge":
            return self.rouge_score(generated, reference)
        elif self.metric == "bleu":
            return self.bleu_score(generated, reference)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
    
    def rouge_score(
        self,
        generated: str,
        reference: str
    ) -> float:
        """计算 ROUGE 分数"""
        # 这里简化实现，实际应使用 rouge 库
        # from rouge import Rouge
        # rouge = Rouge()
        # scores = rouge.get_scores(generated, reference)
        # return scores[0]['rouge-l']['f']
        
        # 简化版本：基于重叠的简单度量
        gen_words = set(generated.lower().split())
        ref_words = set(reference.lower().split())
        
        if len(ref_words) == 0:
            return 0.0
        
        overlap = len(gen_words & ref_words)
        precision = overlap / len(gen_words) if len(gen_words) > 0 else 0
        recall = overlap / len(ref_words)
        
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        return f1
    
    def bleu_score(
        self,
        generated: str,
        reference: str
    ) -> float:
        """计算 BLEU 分数"""
        # 这里简化实现，实际应使用 nltk 或 sacrebleu
        # from nltk.translate.bleu_score import sentence_bleu
        # reference_tokens = reference.split()
        # generated_tokens = generated.split()
        # return sentence_bleu([reference_tokens], generated_tokens)
        
        # 简化版本
        gen_words = generated.lower().split()
        ref_words = reference.lower().split()
        
        if len(gen_words) == 0:
            return 0.0
        
        # 计算 1-gram 准确率
        matches = sum(1 for word in gen_words if word in ref_words)
        return matches / len(gen_words)
```

### 优化器实现（RL 示例）

```python
class REINFORCEO:
    """REINFORCE 优化器"""
    
    def __init__(
        self,
        policy_model,
        learning_rate: float = 1e-4,
        gamma: float = 0.99
    ):
        self.policy_model = policy_model
        self.optimizer = torch.optim.Adam(
            policy_model.parameters(),
            lr=learning_rate
        )
        self.gamma = gamma
    
    def update(
        self,
        rewards: List[float],
        log_probs: List[torch.Tensor]
    ):
        """更新策略模型"""
        # 计算回报
        returns = self._compute_returns(rewards)
        
        # 计算损失
        loss = 0
        for log_prob, R in zip(log_probs, returns):
            loss += -log_prob * R
        
        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def _compute_returns(
        self,
        rewards: List[float]
    ) -> List[float]:
        """计算回报"""
        returns = []
        R = 0
        for r in reversed(rewards):
            R = r + self.gamma * R
            returns.insert(0, R)
        return returns
```

### 完整示例

```python
# 初始化 DSP
evaluator = SummarizationEvaluator(metric="rouge")
rl_optimizer = REINFORCEO(policy_model=policy_model)

dsp = DirectionalStimulusPrompting(
    policy_model_name="gpt2",
    blackbox_model_name="gpt-3.5-turbo",
    evaluator=evaluator,
    rl_optimizer=rl_optimizer
)

# 准备训练数据
training_data = [
    {
        "input": "长文本内容...",
        "ground_truth": "摘要内容..."
    },
    # ... 更多训练样本
]

# 训练
dsp.train(training_data, num_episodes=1000)

# 推理
input_text = "需要摘要的长文本"
stimulus = dsp.generate_stimulus(input_text)
output = dsp.generate_output(input_text, stimulus)

print(f"方向性刺激: {stimulus}")
print(f"生成输出: {output}")
```

## DSP 的优化策略

### 1. 策略 LM 优化

**策略：**
- **模型选择**：选择合适的策略 LM 大小
- **架构设计**：设计高效的模型架构
- **训练策略**：使用合适的训练策略

### 2. 优化策略

**策略：**
- **监督数据**：优先准备高质量训练样本
- **奖励设计**：若使用 RL，设计合理的奖励函数
- **算法选择**：根据任务选择监督学习或 RL
- **超参数调优**：调优训练超参数

### 3. 黑盒 LLM 利用

**策略：**
- **提示设计**：优化提示设计
- **输出格式**：规范输出格式
- **后处理**：添加后处理步骤

### 4. 评估优化

**策略：**
- **多指标评估**：使用多个评估指标
- **人类评估**：结合人类评估
- **自动评估**：使用自动评估工具

## DSP 的局限性

### 1. 训练复杂性

- **挑战**：训练流程可能复杂，RL 尤其不稳定
- **解决方案**：优先使用监督学习，必要时再引入稳定的 RL 算法

### 2. 计算成本

- **挑战**：需要大量计算资源
- **解决方案**：优化计算效率，使用分布式训练

### 3. 评估依赖

- **挑战**：依赖评估指标的质量
- **解决方案**：使用多指标评估，结合人类评估

### 4. 黑盒依赖

- **挑战**：依赖黑盒 LLM 的性能
- **解决方案**：选择强大的黑盒 LLM，优化提示利用

## 最佳实践

### 1. 策略 LM 设计

- **小而精**：使用小而精的策略 LM
- **任务相关**：设计任务相关的架构
- **快速迭代**：支持快速迭代

### 2. 训练方案

- **优先监督学习**：先用监督数据建立稳定基线
- **合理奖励**：若使用 RL，设计合理的奖励函数
- **监控进度**：密切监控训练进度

### 3. 提示设计

- **清晰明确**：确保提示清晰明确
- **方向性强**：强化方向性引导
- **格式统一**：保持格式统一

### 4. 评估管理

- **多维度评估**：多维度评估性能
- **定期验证**：定期验证性能
- **持续改进**：持续改进策略

## DSP 与其他技术的对比

| 特性 | DSP | 标准提示 | Auto-Prompt | CoT |
|------|-----|---------|------------|-----|
| **提示生成** | 策略 LM | 人工 | 自动生成 | 固定 |
| **优化方法** | 监督学习或 RL | 手工 | 搜索/评估 | 手工 |
| **方向性** | 强 | 弱 | 中 | 弱 |
| **适应性** | 高 | 低 | 中 | 低 |
| **计算成本** | 中 | 低 | 高 | 低 |

## 实际应用案例

### 案例 1：新闻摘要

**场景**：生成新闻摘要

**DSP 应用：**
- 策略 LM 生成摘要方向提示
- 引导 LLM 生成符合新闻风格的摘要
- 提高摘要的准确性和可读性

### 案例 2：科学文献摘要

**场景**：生成科学文献摘要

**DSP 应用：**
- 策略 LM 生成学术风格提示
- 引导 LLM 生成学术摘要
- 保持专业性和准确性

### 案例 3：产品评论摘要

**场景**：生成产品评论摘要

**DSP 应用：**
- 策略 LM 生成评论要点提示
- 引导 LLM 提取关键信息
- 生成有意义的摘要

## 评估指标

### 1. 任务性能

- **准确率**：任务完成的准确率
- **质量分数**：输出质量分数
- **一致性**：输出一致性

### 2. 训练效率

- **收敛速度**：训练收敛速度
- **样本效率**：样本使用效率
- **资源消耗**：资源消耗情况

### 3. 提示质量

- **方向性**：提示的方向性
- **有效性**：提示的有效性
- **稳定性**：提示的稳定性

## 相关技术

- **自动提示工程（Auto-Prompt Engineering）**：自动生成提示
- **强化学习（Reinforcement Learning）**：优化方法
- **策略优化（Policy Optimization）**：策略训练
- **黑盒优化（Black-Box Optimization）**：优化黑盒模型
- **提示微调（Prompt Tuning）**：微调提示

## 参考资料

- Li et al. (2023): "Directional Stimulus Prompting"
- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/dsp

## 练习

1. 实现一个简单的 DSP 框架
2. 使用 DSP 优化文本摘要任务
3. 设计不同的奖励函数并比较效果
4. 对比 DSP 和标准提示的性能
5. 实现 DSP 的在线学习版本
