---
category: 前沿技术
difficulty: 专家
type: 前沿技术
year: 2023
author: Shinn et al.
paper_url: https://arxiv.org/abs/2303.11366
applications: 决策任务, 推理任务, 编程任务, 游戏智能体
---

# 自我反思（Reflexion）

## 核心概念

自我反思（Reflexion）是由 Shinn 等人（2023）提出的一个通过语言反馈来强化基于语言的智能体的框架。它是一种"口头"强化的新范例，将策略参数化为智能体的记忆编码与 LLM 的参数选择配对。

### Reflexion 的定义

Reflexion 是一个通过语言反馈强化智能体的框架：
- **语言反馈**：将环境反馈转换为语言反馈（self-reflection）
- **口头强化**：使用自然语言作为强化信号
- **记忆组件**：利用记忆存储经验
- **迭代改进**：通过迭代改进决策和推理

### 核心思想

Reflexion 的核心思想是：
- **反馈转换**：将环境反馈转换为语言反馈
- **自我反思**：智能体反思自己的行为
- **经验学习**：从过去的错误中学习
- **快速改进**：快速有效地改进性能

### 与传统 RL 的区别

| 特性 | 传统 RL | Reflexion |
|------|---------|-----------|
| **反馈形式** | 标量奖励 | 语言反馈 |
| **记忆形式** | 数值记忆 | 语言记忆 |
| **可解释性** | 低 | 高 |
| **数据需求** | 大量 | 少量 |
| **模型微调** | 需要 | 不需要 |
| **反馈细致度** | 粗糙 | 细致 |

## Reflexion 的架构

### 三个核心组件

#### 1. 参与者（Actor）

**作用**：根据状态观测量生成文本和动作

**特点**：
- 生成文本和动作
- 在环境中采取行动
- 接受观察结果
- 形成轨迹

**使用的模型**：
- 链式思考（CoT）
- ReAct 框架

**记忆组件**：
- 短期记忆：当前轨迹
- 长期记忆：历史经验
- 情景记忆：最近轨迹

#### 2. 评估者（Evaluator）

**作用**：对参与者的输出进行评价

**输入**：
- 生成的轨迹（短期记忆）

**输出**：
- 奖励分数

**奖励函数**：
- **决策任务**：使用 LLM 和基于规则的启发式奖励
- **编程任务**：基于测试结果的奖励
- **推理任务**：基于答案准确性的奖励

#### 3. 自我反思（Self-Reflection）

**作用**：生成语言强化线索帮助参与者自我完善

**输入**：
- 奖励信号
- 当前轨迹
- 持久记忆

**输出**：
- 具体且相关的反馈

**存储**：
- 存储在记忆组件中
- 为未来的试验提供上下文

### 架构流程

```
1. 定义任务
   ↓
2. 参与者生成轨迹
   ↓
3. 评估者评估轨迹
   ↓
4. 自我反思生成反馈
   ↓
5. 反馈存储到记忆
   ↓
6. 生成下一条轨迹
   ↓
7. 重复步骤 2-6
```

## Reflexion 的工作流程

### 步骤 1：定义任务

**内容**：
- 定义任务目标
- 定义评估标准
- 定义环境交互规则
- 定义成功条件

**示例**：
```python
task = {
    "description": "在 AlfWorld 环境中完成多步目标",
    "environment": "ALFWorld",
    "success_criteria": "完成任务的所有步骤",
    "max_steps": 50
}
```

### 步骤 2：生成轨迹

**参与者动作**：
```python
def generate_trajectory(actor, state, memory):
    """
    生成轨迹
    """
    trajectory = []
    
    for step in range(max_steps):
        # 获取记忆
        context = memory.get_context()
        
        # 生成思考和行动
        thought, action = actor.generate(state, context)
        
        # 执行行动
        observation, reward, done = environment.step(action)
        
        # 记录轨迹
        trajectory.append({
            "thought": thought,
            "action": action,
            "observation": observation,
            "reward": reward
        })
        
        # 更新状态
        state = observation
        
        if done:
            break
    
    return trajectory
```

### 步骤 3：评估轨迹

**评估者动作**：
```python
def evaluate_trajectory(evaluator, trajectory):
    """
    评估轨迹
    """
    # 计算奖励
    reward = evaluator.compute_reward(trajectory)
    
    # 生成评估
    evaluation = evaluator.evaluate(trajectory)
    
    return {
        "reward": reward,
        "evaluation": evaluation
    }
```

### 步骤 4：执行自我反思

**自我反思动作**：
```python
def self_reflect(reflection_model, trajectory, evaluation, memory):
    """
    执行自我反思
    """
    # 生成反思
    reflection = reflection_model.generate_reflection(
        trajectory=trajectory,
        evaluation=evaluation,
        past_reflections=memory.get_reflections()
    )
    
    # 存储反思
    memory.add_reflection(reflection)
    
    return reflection
```

### 步骤 5：生成下一条轨迹

**参与者使用反思**：
```python
def generate_next_trajectory(actor, state, memory):
    """
    生成下一条轨迹（使用反思）
    """
    # 获取上下文（包括反思）
    context = memory.get_context(include_reflections=True)
    
    # 使用反思生成新的轨迹
    trajectory = generate_trajectory(actor, state, memory)
    
    return trajectory
```

## Reflexion 的实现

### 基础实现框架

```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Step:
    thought: str
    action: str
    observation: str
    reward: float

@dataclass
class Reflection:
    feedback: str
    score: float
    timestamp: int

class Memory:
    """记忆组件"""
    
    def __init__(self, max_capacity: int = 100):
        self.short_term = []  # 短期记忆（当前轨迹）
        self.long_term = []   # 长期记忆（历史经验）
        self.reflections = []  # 自我反思
        self.max_capacity = max_capacity
    
    def add_step(self, step: Step):
        """添加步骤到短期记忆"""
        self.short_term.append(step)
    
    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term = []
    
    def add_reflection(self, reflection: Reflection):
        """添加反思到记忆"""
        self.reflections.append(reflection)
        
        # 限制记忆容量
        if len(self.reflections) > self.max_capacity:
            self.reflections.pop(0)
    
    def get_context(self, include_reflections: bool = True) -> str:
        """获取上下文"""
        context = ""
        
        # 添加最近的反思
        if include_reflections and self.reflections:
            context += "Previous reflections:\n"
            for reflection in self.reflections[-5:]:  # 最近 5 个反思
                context += f"- {reflection.feedback}\n"
            context += "\n"
        
        # 添加长期记忆
        if self.long_term:
            context += "Relevant past experiences:\n"
            for exp in self.long_term[-3:]:  # 最近 3 个经验
                context += f"- {exp}\n"
            context += "\n"
        
        return context

class Actor:
    """参与者"""
    
    def __init__(self, llm, use_cot: bool = True):
        self.llm = llm
        self.use_cot = use_cot
    
    def generate(self, state: str, context: str) -> tuple[str, str]:
        """生成思考和行动"""
        # 构建提示
        prompt = self._build_prompt(state, context)
        
        if self.use_cot:
            # 使用 CoT
            response = self.llm(prompt)
            thought, action = self._parse_cot_response(response)
        else:
            # 直接生成行动
            action = self.llm(prompt)
            thought = ""
        
        return thought, action
    
    def _build_prompt(self, state: str, context: str) -> str:
        """构建提示"""
        prompt = f"Current state: {state}\n\n"
        
        if context:
            prompt += f"Context:\n{context}\n\n"
        
        prompt += "What should I do next? Think step by step."
        
        return prompt
    
    def _parse_cot_response(self, response: str) -> tuple[str, str]:
        """解析 CoT 响应"""
        # 简化实现
        lines = response.split('\n')
        thought = lines[0] if lines else ""
        action = lines[-1] if len(lines) > 1 else ""
        
        return thought, action

class Evaluator:
    """评估者"""
    
    def __init__(self, llm, use_rule_based: bool = False):
        self.llm = llm
        self.use_rule_based = use_rule_based
    
    def compute_reward(self, trajectory: List[Step]) -> float:
        """计算奖励"""
        if self.use_rule_based:
            return self._rule_based_reward(trajectory)
        else:
            return self._llm_based_reward(trajectory)
    
    def _rule_based_reward(self, trajectory: List[Step]) -> float:
        """基于规则的奖励"""
        # 根据任务定义规则
        total_reward = sum(step.reward for step in trajectory)
        return total_reward
    
    def _llm_based_reward(self, trajectory: List[Step]) -> float:
        """基于 LLM 的奖励"""
        # 使用 LLM 评估轨迹质量
        trajectory_text = self._format_trajectory(trajectory)
        
        prompt = f"""
Evaluate the following trajectory and provide a score between 0 and 1:

Trajectory:
{trajectory_text}

Score (0-1):
"""
        
        response = self.llm(prompt)
        
        # 提取分数
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def evaluate(self, trajectory: List[Step]) -> str:
        """评估轨迹"""
        trajectory_text = self._format_trajectory(trajectory)
        
        prompt = f"""
Evaluate the following trajectory and provide feedback:

Trajectory:
{trajectory_text}

Feedback:
"""
        
        feedback = self.llm(prompt)
        return feedback
    
    def _format_trajectory(self, trajectory: List[Step]) -> str:
        """格式化轨迹"""
        text = ""
        for i, step in enumerate(trajectory):
            text += f"Step {i+1}:\n"
            text += f"  Thought: {step.thought}\n"
            text += f"  Action: {step.action}\n"
            text += f"  Observation: {step.observation}\n"
            text += f"  Reward: {step.reward}\n\n"
        return text

class SelfReflection:
    """自我反思"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate_reflection(
        self,
        trajectory: List[Step],
        evaluation: str,
        reward: float,
        past_reflections: List[Reflection]
    ) -> Reflection:
        """生成反思"""
        # 构建提示
        prompt = self._build_reflection_prompt(
            trajectory, evaluation, reward, past_reflections
        )
        
        # 生成反思
        feedback = self.llm(prompt)
        
        # 计算反思分数（基于奖励）
        score = reward
        
        # 创建反思对象
        reflection = Reflection(
            feedback=feedback,
            score=score,
            timestamp=len(past_reflections)
        )
        
        return reflection
    
    def _build_reflection_prompt(
        self,
        trajectory: List[Step],
        evaluation: str,
        reward: float,
        past_reflections: List[Reflection]
    ) -> str:
        """构建反思提示"""
        prompt = "Analyze the following trajectory and provide detailed feedback on what went wrong and how to improve:\n\n"
        
        # 添加轨迹
        prompt += "Trajectory:\n"
        for i, step in enumerate(trajectory):
            prompt += f"Step {i+1}: {step.action} -> {step.observation}\n"
        
        # 添加评估
        prompt += f"\nEvaluation: {evaluation}\n"
        prompt += f"Reward: {reward}\n"
        
        # 添加过去的反思
        if past_reflections:
            prompt += "\nPrevious reflections:\n"
            for ref in past_reflections[-3:]:
                prompt += f"- {ref.feedback}\n"
        
        prompt += "\nYour feedback:"
        
        return prompt

class ReflexionAgent:
    """Reflexion 智能体"""
    
    def __init__(
        self,
        actor: Actor,
        evaluator: Evaluator,
        reflection_model: SelfReflection,
        max_iterations: int = 10
    ):
        self.actor = actor
        self.evaluator = evaluator
        self.reflection_model = reflection_model
        self.max_iterations = max_iterations
        self.memory = Memory()
    
    def run(self, initial_state: str, environment) -> Dict[str, Any]:
        """运行 Reflexion 智能体"""
        best_trajectory = None
        best_reward = float('-inf')
        all_trajectories = []
        
        for iteration in range(self.max_iterations):
            print(f"\nIteration {iteration + 1}/{self.max_iterations}")
            
            # 清空短期记忆
            self.memory.clear_short_term()
            
            # 生成轨迹
            trajectory = self._generate_trajectory(initial_state, environment)
            all_trajectories.append(trajectory)
            
            # 评估轨迹
            evaluation_result = self.evaluator.evaluate(trajectory)
            reward = self.evaluator.compute_reward(trajectory)
            
            print(f"Reward: {reward:.4f}")
            
            # 更新最佳轨迹
            if reward > best_reward:
                best_reward = reward
                best_trajectory = trajectory
            
            # 检查是否达到最佳性能
            if reward >= 1.0:
                print("Achieved perfect performance!")
                break
            
            # 执行自我反思
            reflection = self.reflection_model.generate_reflection(
                trajectory=trajectory,
                evaluation=evaluation_result,
                reward=reward,
                past_reflections=self.memory.reflections
            )
            
            # 存储反思
            self.memory.add_reflection(reflection)
            print(f"Reflection: {reflection.feedback}")
        
        return {
            "best_trajectory": best_trajectory,
            "best_reward": best_reward,
            "all_trajectories": all_trajectories
        }
    
    def _generate_trajectory(self, initial_state: str, environment) -> List[Step]:
        """生成轨迹"""
        trajectory = []
        state = initial_state
        done = False
        max_steps = 50
        
        for step in range(max_steps):
            # 获取上下文
            context = self.memory.get_context()
            
            # 生成思考和行动
            thought, action = self.actor.generate(state, context)
            
            # 执行行动
            observation, reward, done = environment.step(action)
            
            # 记录步骤
            step_obj = Step(
                thought=thought,
                action=action,
                observation=observation,
                reward=reward
            )
            trajectory.append(step_obj)
            
            # 添加到短期记忆
            self.memory.add_step(step_obj)
            
            # 更新状态
            state = observation
            
            if done:
                break
        
        return trajectory
```

## Reflexion 的性能表现

### 决策任务（AlfWorld）

**评估结果：**
- ReAct + Reflexion：130/134 任务完成（97.0%）
- ReAct：显著低于 Reflexion

**关键发现：**
- 使用启发式和 GPT 的自我评估
- 完成率显著提高
- 在多个环境中表现优异

### 推理任务（HotPotQA）

**评估结果：**
- Reflexion + CoT：优于仅 CoT
- Reflexion + CoT + 情景记忆：优于具有情景记忆的 CoT

**关键发现：**
- 在几个学习步骤中显著优于基线
- 添加情景记忆后性能进一步提升
- 推理能力明显改善

### 编程任务（HumanEval、MBPP、LeetCode Hard）

**评估结果：**
- **Python**：在 HumanEval 和 MBPP 上优于之前的 SOTA
- **Rust**：在 LeetCode Hard 上表现优异
- **多种语言**：在 Python 和 Rust 上都表现出色

**关键发现：**
- 编程能力显著提升
- 测试驱动开发方法有效
- 某些情况下达到 SOTA 水平

## Reflexion 的优势

### 1. 语言反馈

- **细致反馈**：比标量奖励更细致和具体
- **可解释**：反馈内容易于理解
- **针对性**：可以针对性地改进

### 2. 记忆机制

- **短期记忆**：存储当前轨迹
- **长期记忆**：存储历史经验
- **情景记忆**：存储最近轨迹
- **反思记忆**：存储自我反思

### 3. 快速学习

- **少样本学习**：只需要少量样本
- **快速迭代**：快速迭代改进
- **高效利用**：高效利用经验

### 4. 不需要微调

- **零样本**：不需要微调底层模型
- **轻量级**：轻量级替代方案
- **资源高效**：节省计算资源

## Reflexion 的适用场景

### 何时使用 Reflexion

#### 1. 智能体需要从尝试和错误中学习

**场景**：
- 决策任务
- 推理任务
- 编程任务

**原因**：
- 反思过去的错误
- 将知识纳入未来决策
- 通过反复试验学习

#### 2. 传统的强化学习方法失效

**场景**：
- 数据有限
- 计算资源有限
- 需要快速迭代

**原因**：
- 不需要大量训练数据
- 不需要昂贵的模型微调
- 更高效的数据和计算资源利用

#### 3. 需要细致入微的反馈

**场景**：
- 需要详细反馈的任务
- 需要具体改进建议的任务
- 需要可解释反馈的任务

**原因**：
- 语言反馈比标量奖励更细致
- 更好地了解错误
- 更有针对性的改进

#### 4. 可解释性和直接记忆很重要

**场景**：
- 需要分析学习过程
- 需要理解决策过程
- 需要可解释的 AI

**原因**：
- 提供更可解释的记忆形式
- 情景记忆直接可见
- 学习过程易于分析

### 有效的任务类型

#### 1. 序列决策

**任务**：在各种环境中导航并完成多步目标

**示例**：
- AlfWorld
- 文本游戏
- 规划任务

#### 2. 推理

**任务**：需要对多个文档进行推理的问答

**示例**：
- HotPotQA
- 多跳问答
- 复杂推理

#### 3. 编程

**任务**：编写和调试代码

**示例**：
- HumanEval
- MBPP
- LeetCode

## Reflexion 的局限性

### 1. 依赖自我评估能力

**挑战**：
- 需要智能体准确评估其表现
- 需要产生有用的反思
- 复杂任务更具挑战性

**解决方案**：
- 使用更强大的 LLM
- 结合多种评估方法
- 逐步提高评估能力

### 2. 长期记忆限制

**挑战**：
- 使用最大容量的滑动窗口
- 对于复杂任务可能不够
- 难以处理大量历史信息

**解决方案**：
- 使用向量嵌入
- 使用 SQL 数据库
- 使用更高级的记忆结构

### 3. 代码生成限制

**挑战**：
- 测试驱动开发在指定准确的输入输出映射方面存在限制
- 受硬件影响的非确定性生成器函数
- 函数输出的不确定性

**解决方案**：
- 改进测试用例设计
- 考虑环境因素
- 添加更多测试场景

## 最佳实践

### 1. 参与者设计

- **CoT 集成**：集成链式思考
- **ReAct 集成**：集成 ReAct 框架
- **记忆利用**：充分利用记忆组件

### 2. 评估者设计

- **奖励设计**：设计合理的奖励函数
- **评估细致**：提供细致的评估
- **多种方法**：结合多种评估方法

### 3. 自我反思设计

- **反馈具体**：提供具体的反馈
- **建议可行**：提供可行的建议
- **上下文相关**：与上下文相关

### 4. 记忆管理

- **容量管理**：管理记忆容量
- **信息筛选**：筛选重要信息
- **定期清理**：定期清理无用信息

## Reflexion 与其他技术的对比

| 特性 | Reflexion | 传统 RL | ReAct | CoT |
|------|-----------|---------|-------|-----|
| **反馈形式** | 语言反馈 | 标量奖励 | 观察/思考 | 思考 |
| **记忆形式** | 语言记忆 | 数值记忆 | 轨迹 | 轨迹 |
| **可解释性** | 高 | 低 | 中 | 中 |
| **数据需求** | 少量 | 大量 | 中等 | 中等 |
| **模型微调** | 不需要 | 需要 | 不需要 | 不需要 |
| **自我改进** | 强 | 中 | 弱 | 弱 |

## 实际应用案例

### 案例 1：游戏智能体

**场景**：在文本游戏中导航

**Reflexion 应用：**
- 智能体尝试不同的行动
- 反思失败的原因
- 改进策略
- 最终完成游戏

### 案例 2：代码生成

**场景**：生成和调试代码

**Reflexion 应用：**
- 生成代码
- 运行测试
- 反思错误
- 修复代码

### 案例 3：问答系统

**场景**：回答复杂问题

**Reflexion 应用：**
- 尝试回答
- 验证答案
- 反思错误
- 改进回答

## 评估指标

### 1. 任务性能

- **成功率**：任务完成的成功率
- **准确率**：答案的准确率
- **效率**：完成任务所需的步骤

### 2. 学习效率

- **收敛速度**：达到最佳性能所需的迭代次数
- **样本效率**：达到最佳性能所需的样本数量
- **改进速度**：性能提升的速度

### 3. 反思质量

- **反馈准确性**：反馈的准确性
- **建议可行性**：建议的可行性
- **改进效果**：反思带来的改进效果

## 相关技术

- **强化学习（Reinforcement Learning）**：基础理论
- **链式思考（Chain-of-Thought）**：推理方法
- **ReAct 框架**：交互框架
- **记忆增强神经网络（Memory-Augmented Neural Networks）**：记忆机制
- **元学习（Meta-Learning）**：学习如何学习

## 参考资料

- Shinn et al. (2023): "Reflexion: Language Agents with Verbal Reinforcement Learning"
- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/reflexion

## 练习

1. 实现一个简单的 Reflexion 框架
2. 使用 Reflexion 解决 AlfWorld 任务
3. 设计不同的自我反思策略
4. 对比 Reflexion 和 ReAct 的性能
5. 实现 Reflexion 的不同记忆结构