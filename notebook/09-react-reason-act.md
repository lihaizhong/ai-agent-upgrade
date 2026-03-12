---
category: 工具使用
difficulty: 高级
type: 工具技术
year: 2022
author: Yao et al.
paper_url: https://arxiv.org/abs/2210.03629
applications: 问答系统, 事实验证, 环境交互, 代码生成
---

# ReAct 框架（Reasoning and Acting）

## 核心概念

ReAct 框架是由 Yao 等人（2022）引入的一个框架，其中 LLMs 以交错的方式生成**推理轨迹**（Reasoning Traces）和**任务特定操作**（Task-Specific Actions）。

### ReAct 的定义

ReAct 是一个将推理和行为与 LLMs 相结合的通用范例：
- **推理轨迹**：生成口头推理轨迹来诱导、跟踪和更新操作计划
- **任务操作**：执行与外部源（如知识库或环境）交互的操作
- **信息收集**：收集信息来支持推理过程

### 核心思想

ReAct 的灵感来自于"行为"和"推理"之间的协同作用：
- **推理**：分解问题、提取信息、执行常识或算术推理
- **行动**：与外部环境交互（如搜索引擎、数据库）
- **观察**：接收外部环境的反馈
- **迭代**：基于观察结果更新推理和行动

### 与 CoT 的区别

| 特性 | 链式思考（CoT） | ReAct |
|------|----------------|-------|
| **推理形式** | 内部推理 | 推理 + 行动 |
| **外部交互** | 无 | 有 |
| **信息更新** | 无 | 有 |
| **事实验证** | 可能幻觉 | 可验证 |
| **灵活性** | 高 | 中（结构性约束） |

## ReAct 的工作原理

### 工作流程

```
1. 接收任务/问题
   ↓
2. 生成推理轨迹（思考）
   ↓
3. 执行操作（行动）
   ↓
4. 接收观察结果（观察）
   ↓
5. 更新推理（思考）
   ↓
6. 重复步骤 2-5 直到得到答案
   ↓
7. 输出最终答案
```

### 核心组件

#### 1. 思考（Thought）

- **分解问题**：将复杂问题分解为子问题
- **提取信息**：从观察中提取关键信息
- **执行推理**：进行常识或算术推理
- **规划行动**：确定下一步的操作

#### 2. 行动（Action）

- **搜索信息**：搜索外部知识库
- **查询数据**：查询数据库或 API
- **计算操作**：执行计算任务
- **环境交互**：与环境进行交互

#### 3. 观察（Observation）

- **接收结果**：接收操作的结果
- **验证信息**：验证信息的准确性
- **更新状态**：更新问题的状态
- **调整策略**：根据观察调整策略

## ReAct 提示示例

### 知识密集型任务示例

**问题：**
```
除了苹果遥控器，还有哪些设备可以控制苹果遥控器最初设计用来交互的程序?
```

**ReAct 轨迹：**
```
问题: 除了苹果遥控器，还有哪些设备可以控制苹果遥控器最初设计用来交互的程序?

思考 1: 我需要先了解苹果遥控器最初设计用来交互的是什么程序。
操作 1: 搜索 [苹果遥控器 设计 交互 程序]

观察 1: 苹果遥控器最初设计用于与 Apple TV 交互，控制媒体播放和其他功能。

思考 2: 现在我需要找出还有哪些设备可以控制 Apple TV。
操作 2: 搜索 [设备 控制 Apple TV]

观察 2: 可以控制 Apple TV 的设备包括 iPhone、iPad、Apple Watch、Mac、AirPods 等。

思考 3: 我需要确认这些设备都可以通过遥控器功能控制 Apple TV。
操作 3: 搜索 [iPhone iPad Apple Watch 控制 Apple TV 遥控器]

观察 3: 是的，iPhone、iPad、Apple Watch 都可以通过内置的遥控器应用或 AirPlay 功能控制 Apple TV。Mac 也可以通过遥控器应用控制 Apple TV。

思考 4: 我已经得到了答案。除了苹果遥控器，还有 iPhone、iPad、Apple Watch、Mac 可以控制 Apple TV。
操作 4: 结束 [iPhone、iPad、Apple Watch、Mac]
```

### 地理问题示例

**问题：**
```
科罗拉多造山带东部区域延伸到的区域的海拔范围是多少?
```

**ReAct 轨迹：**
```
思考 1: 我需要搜索科罗拉多造山带，找到科罗拉多造山带东段延伸的区域，然后找到该区域的海拔范围。
操作 1: 搜索 [科罗拉多造山带]

观察 1: 科罗拉多造山带是科罗拉多及其周边地区造山运动的一段。

思考 2: 它没有提到东部地区。所以我需要查一下东部地区。
操作 2: 查找 [东部地区]

观察 2: 东部区域延伸至高平原，称为中原造山带。

思考 3: 科罗拉多造山运动的东部区域延伸到高平原。所以我需要搜索高平原，找到它的海拔范围。
操作 3: 搜索 [高平原]

观察 3: 高平原指的是两个截然不同的陆地区域之一。

思考 4: 我需要搜索高平原（美国）
操作 4: 搜索 [高平原（美国）]

观察 4: 高平原是大平原的一个分区。从东到西，高平原的海拔从 1800 到 7000 英尺 (550 到 2130 米) 不等。

思考 5: 高平原海拔高度从 1800 到 7000 英尺，所以答案是 1800 到 7000 英尺。
操作 5: 结束 [1800 到 7000 英尺]
```

## ReAct 的提示设计

### 少样本提示设计

**步骤 1：** 从训练集选择案例，组成 ReAct 格式的轨迹

**步骤 2：** 将轨迹作为少样本示例添加到提示中

**轨迹组成：**
```
问题: [问题描述]
思考 1: [推理]
操作 1: [操作]
观察 1: [观察结果]
思考 2: [推理]
操作 2: [操作]
观察 2: [观察结果]
...
思考 N: [最终推理]
操作 N: 结束 [答案]
```

### 不同任务的提示设计

#### 推理为主的任务（如 HotpotQA）

- **特点**：多思考-操作-观察步骤
- **用途**：复杂推理任务
- **示例数量**：多个完整示例

#### 决策为主的任务（如 ALFWorld）

- **特点**：较少使用思考，更多操作
- **用途**：环境交互任务
- **示例数量**：简化的示例

## ReAct 的性能表现

### 知识密集型任务

#### 评估任务

- **HotpotQA**：多跳问答任务
- **Fever**：事实验证任务

#### 评估结果

| 方法 | HotpotQA | Fever |
|------|----------|-------|
| Act（仅操作） | 基线 | 基线 |
| CoT（链式思考） | 最高 | 较高 |
| ReAct | 高 | 最高 |
| ReAct + CoT | 最高 | 最高 |

#### 关键发现

1. **ReAct vs Act**：ReAct 优于 Act
2. **ReAct vs CoT**：
   - 在 Fever 上优于 CoT
   - 在 HotpotQA 上略低于 CoT
3. **最佳方法**：ReAct + CoT + 自我一致性

#### 误差分析

**CoT 的问题：**
- 事实幻觉
- 无法更新知识
- 错误传播

**ReAct 的问题：**
- 结构性约束降低了灵活性
- 依赖检索信息
- 非信息性搜索结果阻碍推理

### 决策型任务

#### 评估任务

- **ALFWorld**：基于文本的游戏环境
- **WebShop**：在线购物网站环境

#### 评估结果

| 方法 | ALFWorld | WebShop |
|------|----------|---------|
| Act（仅操作） | 基线 | 基线 |
| ReAct | 优于 Act | 优于 Act |

#### 关键发现

1. **ReAct 的优势**：能够正确分解目标
2. **Act 的局限**：不能正确分解子目标
3. **差距**：与人类专家仍有差距

## ReAct 的优势

### 1. 解决事实幻觉

- **验证机制**：通过外部验证避免幻觉
- **信息更新**：动态更新知识
- **可追溯性**：推理过程可追溯

### 2. 提高可解释性

- **透明推理**：推理过程可见
- **人类可读**：推理轨迹易于理解
- **可信度**：提高模型的可信度

### 3. 增强适应性

- **环境交互**：适应不同环境
- **动态调整**：根据观察调整策略
- **错误恢复**：从错误中恢复

### 4. 扩展能力

- **工具集成**：集成各种工具
- **知识访问**：访问外部知识
- **复杂任务**：处理复杂任务

## ReAct 的实现

### 使用 LangChain 实现

#### 安装依赖

```bash
pip install --upgrade openai
pip install --upgrade langchain
pip install --upgrade python-dotenv
pip install google-search-results
```

#### 导入库

```python
import openai
import os
from langchain.llms import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from dotenv import load_dotenv

load_dotenv()

# 设置 API keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
```

#### 配置 LLM 和工具

```python
# 配置 LLM
llm = OpenAI(model_name="text-davinci-003", temperature=0)

# 加载工具
tools = load_tools(["google-serper", "llm-math"], llm=llm)

# 初始化代理
agent = initialize_agent(
    tools, 
    llm, 
    agent="zero-shot-react-description", 
    verbose=True
)
```

#### 运行代理

```python
# 执行查询
query = "奥利维亚·王尔德的男朋友是谁?他现在的年龄的0.23次方是多少?"
result = agent.run(query)

print(result)
```

#### 执行过程

```
> 正在输入新代理执行器链......

思考: 我得查出奥利维亚·王尔德的男友是谁然后计算出他的年龄的 0.23 次方。
操作: 搜索
操作输入: "奥利维亚·王尔德的男友"

观察: 奥利维亚·王尔德与杰森·苏代基斯在多年前订婚，在他们分手后，她开始与哈里·斯泰尔斯约会。

思考: 我需要找出哈里·斯泰尔斯的年龄。
操作: 搜索
操作输入: "哈里·斯泰尔斯的年龄"

观察: 29 岁

思考: 我需要计算 29 的 0.23 次方。
操作: 计算器
操作输入: 29^0.23

观察: 答案: 2.169459462491557

思考: 现在我知道最终答案了。
最终答案: 哈里·斯泰尔斯, 奥利维亚·王尔德的男朋友, 29 岁。他年龄的 0.23 次方是 2.169459462491557。

> 结束链。
```

#### 输出结果

```
哈里·斯泰尔斯, 奥利维亚·王尔德的男朋友, 29 岁。他年龄的 0.23 次方是 2.169459462491557。
```

### 自定义 ReAct 实现

```python
class ReActAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.max_steps = 10
    
    def run(self, question):
        trajectory = []
        step = 0
        
        while step < self.max_steps:
            # 生成思考
            thought = self.generate_thought(question, trajectory)
            trajectory.append({"type": "thought", "content": thought})
            
            # 检查是否结束
            if "结束" in thought or "答案" in thought:
                break
            
            # 生成操作
            action = self.generate_action(question, trajectory)
            trajectory.append({"type": "action", "content": action})
            
            # 执行操作
            observation = self.execute_action(action)
            trajectory.append({"type": "observation", "content": observation})
            
            step += 1
        
        return trajectory
    
    def generate_thought(self, question, trajectory):
        prompt = self.build_thought_prompt(question, trajectory)
        return self.llm(prompt)
    
    def generate_action(self, question, trajectory):
        prompt = self.build_action_prompt(question, trajectory)
        return self.llm(prompt)
    
    def execute_action(self, action):
        # 根据操作类型执行相应的工具
        # 这里简化实现
        return f"执行操作: {action}"
    
    def build_thought_prompt(self, question, trajectory):
        # 构建思考提示
        return f"问题: {question}\n轨迹: {trajectory}\n思考:"
    
    def build_action_prompt(self, question, trajectory):
        # 构建操作提示
        return f"问题: {question}\n轨迹: {trajectory}\n操作:"
```

## ReAct 的应用场景

### 1. 问答系统

**场景**：回答需要外部信息的复杂问题

**ReAct 应用：**
- 搜索知识库
- 验证信息
- 综合答案

### 2. 事实验证

**场景**：验证事实的真实性

**ReAct 应用：**
- 搜索证据
- 对比信息
- 判断真假

### 3. 决策支持

**场景**：支持复杂决策过程

**ReAct 应用：**
- 收集信息
- 分析选项
- 做出决策

### 4. 环境交互

**场景**：与复杂环境交互

**ReAct 应用：**
- 探索环境
- 执行操作
- 达成目标

### 5. 代码生成

**场景**：生成需要外部信息的代码

**ReAct 应用：**
- 搜索文档
- 查找示例
- 生成代码

## ReAct 的局限性

### 1. 结构性约束

- **挑战**：结构化约束降低了灵活性
- **解决方案**：优化结构设计，增加灵活性

### 2. 依赖外部信息

- **挑战**：高度依赖检索信息
- **解决方案**：优化检索策略，提高信息质量

### 3. 错误恢复困难

- **挑战**：非信息性搜索结果难以恢复
- **解决方案**：设计错误恢复机制

### 4. 计算成本

- **挑战**：需要多次查询外部工具
- **解决方案**：优化查询策略，缓存结果

## 最佳实践

### 1. 提示设计

- **高质量示例**：使用高质量的少样本示例
- **多样化场景**：覆盖不同的应用场景
- **清晰格式**：保持清晰的格式

### 2. 工具选择

- **合适工具**：选择合适的工具
- **工具组合**：组合多种工具
- **性能优化**：优化工具性能

### 3. 推理控制

- **步骤限制**：限制最大步骤数
- **质量检查**：检查推理质量
- **提前终止**：合理提前终止

### 4. 错误处理

- **错误检测**：检测错误
- **错误恢复**：从错误中恢复
- **重试机制**：实现重试机制

## ReAct 与其他技术的对比

| 特性 | ReAct | CoT | RAG | 工具使用 |
|------|-------|-----|-----|---------|
| **外部交互** | 有 | 无 | 有 | 有 |
| **推理过程** | 显式 | 显式 | 隐式 | 隐式 |
| **信息更新** | 动态 | 静态 | 动态 | 动态 |
| **可解释性** | 高 | 高 | 中 | 中 |
| **灵活性** | 中 | 高 | 高 | 中 |
| **适用场景** | 复杂推理 | 纯推理 | 知识检索 | 工具调用 |

## 实际应用案例

### 案例 1：学术研究

**场景**：辅助学术研究

**ReAct 应用：**
- 搜索文献
- 查找数据
- 分析结果

**效果：**
- 提高研究效率
- 减少信息遗漏
- 增强研究质量

### 案例 2：客户服务

**场景**：智能客服系统

**ReAct 应用：**
- 理解问题
- 查找信息
- 提供答案

**效果：**
- 提高服务质量
- 减少响应时间
- 增强客户满意度

### 案例 3：教育辅导

**场景**：智能教育辅导

**ReAct 应用：**
- 理解问题
- 查找知识
- 提供解答

**效果：**
- 个性化辅导
- 提高学习效果
- 增强学习兴趣

## 评估指标

### 1. 任务性能

- **准确率**：任务完成的准确率
- **成功率**：任务完成的成功率
- **效率**：任务完成的效率

### 2. 推理质量

- **逻辑性**：推理的逻辑性
- **连贯性**：推理的连贯性
- **有效性**：推理的有效性

### 3. 工具使用

- **工具选择**：工具选择的合理性
- **操作效率**：操作的效率
- **资源利用**：资源的利用率

## 相关技术

- **思维链提示（Chain-of-Thought）**：基础推理技术
- **RAG（检索增强生成）**：知识检索技术
- **工具使用（Tool Use）**：工具调用技术
- **PAL（程序辅助语言模型）**：程序执行技术
- **ART（自动推理和工具使用）**：自动化框架

## 参考资料

- Yao et al. (2022): "ReAct: Synergizing Reasoning and Acting in Language Models"
- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/react
- LangChain Documentation: https://python.langchain.com/
- GitHub 代码: https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/react.ipynb

## 练习

1. 使用 LangChain 实现一个简单的 ReAct 代理
2. 实现自定义的 ReAct 框架
3. 使用 ReAct 解决复杂的问答问题
4. 对比 ReAct 和 CoT 在不同任务上的表现
5. 优化 ReAct 的提示设计和工具选择