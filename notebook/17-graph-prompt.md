---
category: 前沿技术
difficulty: 专家
type: 前沿技术
year: 2023
author: Liu et al.
paper_url: https://arxiv.org/abs/2302.08043
applications: 图分类, 节点分类, 链路预测, 知识图谱
---

# GraphPrompt（图提示）

## 核心概念

GraphPrompt 是由 Liu 等人（2023）提出的一种新的图提示框架，旨在统一图神经网络的预训练与下游任务适配。这是一个将提示学习与图神经网络（Graph Neural Networks, GNNs）相结合的方法。

### GraphPrompt 的定义

GraphPrompt 是一个图提示框架：
- **图结构输入**：处理图结构数据
- **提示学习**：使用提示学习范式
- **下游任务**：提高下游任务性能
- **跨任务泛化**：支持跨任务泛化

### 核心思想

GraphPrompt 的核心思想是：
- **图提示**：在图结构上应用提示技术
- **预训练提示**：利用预训练模型和提示
- **任务适应**：通过提示适应不同任务
- **性能提升**：提高下游任务性能

### 与传统方法的对比

| 特性 | 传统 GNN | GraphPrompt |
|------|----------|-------------|
| **任务适应** | 需要微调 | 仅需提示 |
| **数据需求** | 大量标注数据 | 少量标注数据 |
| **跨任务泛化** | 有限 | 强 |
| **模型更新** | 更新模型参数 | 更新提示 |
| **计算成本** | 高 | 低 |

## GraphPrompt 的架构

### 核心组件

#### 1. 图编码器（Graph Encoder）

**作用**：编码图结构数据

**输入**：
- 节点特征
- 边特征
- 图结构

**输出**：
- 节点嵌入
- 图嵌入

#### 2. 提示生成器（Prompt Generator）

**作用**：生成任务特定的提示

**输入**：
- 图嵌入
- 任务描述
- 少量样本

**输出**：
- 提示向量
- 提示模板

#### 3. 提示融合器（Prompt Fusion）

**作用**：融合提示和图特征

**输入**：
- 图嵌入
- 提示向量

**输出**：
- 融合特征
- 上下文特征

#### 4. 任务预测器（Task Predictor）

**作用**：根据融合特征进行预测

**输入**：
- 融合特征
- 任务信息

**输出**：
- 预测结果

### 架构流程

```
图输入
├── 节点特征
├── 边特征
└── 图结构
    ↓
图编码器
    ↓
图嵌入
    ↓
提示生成器
├── 任务描述
├── 少量样本
└── 提示模板
    ↓
提示向量
    ↓
提示融合器
├── 图嵌入
└── 提示向量
    ↓
融合特征
    ↓
任务预测器
    ↓
预测结果
```

## GraphPrompt 的工作原理

### 步骤 1：图编码

**目的**：将图结构数据编码为向量表示

**过程**：
1. 提取节点特征
2. 提取边特征
3. 应用图神经网络
4. 生成图嵌入

### 步骤 2：提示生成

**目的**：生成任务特定的提示

**过程**：
1. 分析任务描述
2. 参考少量样本
3. 生成提示向量
4. 创建提示模板

### 步骤 3：提示融合

**目的**：融合提示和图特征

**过程**：
1. 对齐提示向量和图嵌入
2. 应用融合机制
3. 生成融合特征
4. 增强上下文信息

### 步骤 4：任务预测

**目的**：根据融合特征进行预测

**过程**：
1. 提取任务相关信息
2. 应用预测模型
3. 生成预测结果
4. 输出最终答案

## GraphPrompt 的实现

### 基础实现框架

下面的代码是便于理解核心机制的示意实现，不等同于论文中的原始实现细节。

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
import torch_geometric
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool

class GraphEncoder(nn.Module):
    """图编码器"""
    
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 256,
        output_dim: int = 256,
        num_layers: int = 3,
        gnn_type: str = "gcn"
    ):
        super().__init__()
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # 构建 GNN 层
        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        
        if gnn_type == "gcn":
            conv_class = GCNConv
        elif gnn_type == "gat":
            conv_class = GATConv
        else:
            raise ValueError(f"Unknown GNN type: {gnn_type}")
        
        # 第一层
        self.convs.append(conv_class(input_dim, hidden_dim))
        self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # 中间层
        for _ in range(num_layers - 2):
            self.convs.append(conv_class(hidden_dim, hidden_dim))
            self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # 最后一层
        self.convs.append(conv_class(hidden_dim, output_dim))
        self.bns.append(nn.BatchNorm1d(output_dim))
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """前向传播"""
        for i, (conv, bn) in enumerate(zip(self.convs, self.bns)):
            x = conv(x, edge_index)
            x = bn(x)
            
            if i < self.num_layers - 1:
                x = F.relu(x)
                x = F.dropout(x, p=0.5, training=self.training)
        
        # 图级池化
        if batch is not None:
            x = global_mean_pool(x, batch)
        
        return x

class PromptGenerator(nn.Module):
    """提示生成器"""
    
    def __init__(
        self,
        graph_dim: int,
        prompt_dim: int = 256,
        num_prompts: int = 10
    ):
        super().__init__()
        self.num_prompts = num_prompts
        
        # 提示向量（可学习参数）
        self.prompt_vectors = nn.Parameter(
            torch.randn(num_prompts, prompt_dim)
        )
        
        # 投影层
        self.graph_to_prompt = nn.Linear(graph_dim, prompt_dim)
        self.prompt_fusion = nn.MultiheadAttention(
            prompt_dim,
            num_heads=8,
            batch_first=True
        )
    
    def forward(
        self,
        graph_embedding: torch.Tensor,
        task_description: Optional[str] = None
    ) -> torch.Tensor:
        """生成提示向量"""
        batch_size = graph_embedding.size(0)
        
        # 投影图嵌入到提示空间
        graph_proj = self.graph_to_prompt(graph_embedding)
        
        # 扩展提示向量
        prompts = self.prompt_vectors.unsqueeze(0).expand(
            batch_size, -1, -1
        )
        
        # 使用注意力机制融合
        query = graph_proj.unsqueeze(1)
        key = prompts
        value = prompts
        
        attended, _ = self.prompt_fusion(query, key, value)
        
        # 返回融合后的提示
        prompt_vector = attended.squeeze(1)
        
        return prompt_vector
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示模板"""
        templates = {
            "node_classification": "Classify each node based on its features and connections.",
            "graph_classification": "Classify the entire graph based on its structure and features.",
            "link_prediction": "Predict whether there is a link between two nodes.",
            "node_clustering": "Cluster nodes into groups based on their features and connections."
        }
        
        return templates.get(task_type, "Perform the task on the graph.")

class PromptFusion(nn.Module):
    """提示融合器"""
    
    def __init__(
        self,
        graph_dim: int,
        prompt_dim: int,
        output_dim: int = 256
    ):
        super().__init__()
        
        # 投影层
        self.graph_proj = nn.Linear(graph_dim, output_dim)
        self.prompt_proj = nn.Linear(prompt_dim, output_dim)
        
        # 融合机制
        self.fusion = nn.Sequential(
            nn.Linear(output_dim * 2, output_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(output_dim, output_dim)
        )
        
        # 门控机制
        self.gate = nn.Sequential(
            nn.Linear(output_dim * 2, output_dim),
            nn.Sigmoid()
        )
    
    def forward(
        self,
        graph_embedding: torch.Tensor,
        prompt_vector: torch.Tensor
    ) -> torch.Tensor:
        """融合提示和图特征"""
        # 投影到相同维度
        graph_proj = self.graph_proj(graph_embedding)
        prompt_proj = self.prompt_proj(prompt_vector)
        
        # 拼接特征
        concat_features = torch.cat([graph_proj, prompt_proj], dim=-1)
        
        # 计算门控
        gate = self.gate(concat_features)
        
        # 融合特征
        fused = self.fusion(concat_features)
        
        # 应用门控
        gated_fusion = gate * fused + (1 - gate) * graph_proj
        
        return gated_fusion

class TaskPredictor(nn.Module):
    """任务预测器"""
    
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 256,
        num_classes: int = 2,
        task_type: str = "graph_classification"
    ):
        super().__init__()
        self.task_type = task_type
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, num_classes)
        )
    
    def forward(
        self,
        fused_features: torch.Tensor,
        node_features: Optional[torch.Tensor] = None,
        edge_index: Optional[torch.Tensor] = None,
        batch: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """前向传播"""
        if self.task_type == "graph_classification":
            # 图级分类
            logits = self.classifier(fused_features)
        
        elif self.task_type == "node_classification":
            # 节点级分类
            if node_features is not None and batch is not None:
                # 广播图级特征到节点级
                batch_size = fused_features.size(0)
                num_nodes = node_features.size(0)
                
                # 为每个节点分配对应的图特征
                node_graph_features = fused_features[batch]
                
                # 融合节点特征和图特征
                node_fused = torch.cat([node_features, node_graph_features], dim=-1)
                logits = self.classifier(node_fused)
            else:
                logits = self.classifier(fused_features)
        
        else:
            # 其他任务类型
            logits = self.classifier(fused_features)
        
        return logits

class GraphPrompt(nn.Module):
    """GraphPrompt 模型"""
    
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 256,
        output_dim: int = 256,
        num_classes: int = 2,
        num_prompts: int = 10,
        task_type: str = "graph_classification",
        gnn_type: str = "gcn"
    ):
        super().__init__()
        
        # 图编码器
        self.graph_encoder = GraphEncoder(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            output_dim=output_dim,
            gnn_type=gnn_type
        )
        
        # 提示生成器
        self.prompt_generator = PromptGenerator(
            graph_dim=output_dim,
            prompt_dim=output_dim,
            num_prompts=num_prompts
        )
        
        # 提示融合器
        self.prompt_fusion = PromptFusion(
            graph_dim=output_dim,
            prompt_dim=output_dim,
            output_dim=output_dim
        )
        
        # 任务预测器
        self.task_predictor = TaskPredictor(
            input_dim=output_dim,
            hidden_dim=hidden_dim,
            num_classes=num_classes,
            task_type=task_type
        )
        
        self.task_type = task_type
    
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None,
        task_description: Optional[str] = None
    ) -> torch.Tensor:
        """前向传播"""
        # 图编码
        graph_embedding = self.graph_encoder(x, edge_index, batch)
        
        # 生成提示
        prompt_vector = self.prompt_generator(graph_embedding, task_description)
        
        # 融合提示
        fused_features = self.prompt_fusion(graph_embedding, prompt_vector)
        
        # 任务预测
        if self.task_type == "node_classification":
            logits = self.task_predictor(
                fused_features,
                node_features=x,
                edge_index=edge_index,
                batch=batch
            )
        else:
            logits = self.task_predictor(fused_features)
        
        return logits
    
    def pretrain(
        self,
        dataloader,
        num_epochs: int = 100,
        learning_rate: float = 0.001
    ):
        """预训练"""
        optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        for epoch in range(num_epochs):
            self.train()
            total_loss = 0
            
            for batch in dataloader:
                optimizer.zero_grad()
                
                # 前向传播
                logits = self(
                    batch.x,
                    batch.edge_index,
                    batch.batch
                )
                
                # 计算损失
                loss = criterion(logits, batch.y)
                
                # 反向传播
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {total_loss / len(dataloader):.4f}")
    
    def adapt_to_task(
        self,
        task_type: str,
        few_shot_samples: List,
        num_epochs: int = 50,
        learning_rate: float = 0.0001
    ):
        """适应新任务"""
        # 冻结图编码器
        for param in self.graph_encoder.parameters():
            param.requires_grad = False
        
        # 更新任务类型
        self.task_type = task_type
        
        # 只训练提示生成器和融合器
        optimizer = torch.optim.Adam(
            list(self.prompt_generator.parameters()) +
            list(self.prompt_fusion.parameters()),
            lr=learning_rate
        )
        
        criterion = nn.CrossEntropyLoss()
        
        for epoch in range(num_epochs):
            self.train()
            total_loss = 0
            
            for batch in few_shot_samples:
                optimizer.zero_grad()
                
                # 前向传播
                logits = self(
                    batch.x,
                    batch.edge_index,
                    batch.batch
                )
                
                # 计算损失
                loss = criterion(logits, batch.y)
                
                # 反向传播
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if epoch % 10 == 0:
                print(f"Adaptation Epoch {epoch}, Loss: {total_loss / len(few_shot_samples):.4f}")
```

### 训练和评估

```python
def train_graphprompt(
    model: GraphPrompt,
    train_loader,
    val_loader,
    num_epochs: int = 100,
    learning_rate: int = 0.001
):
    """训练 GraphPrompt 模型"""
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    
    best_val_acc = 0
    
    for epoch in range(num_epochs):
        # 训练
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for batch in train_loader:
            optimizer.zero_grad()
            
            logits = model(
                batch.x,
                batch.edge_index,
                batch.batch
            )
            
            loss = criterion(logits, batch.y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
            # 计算准确率
            pred = logits.argmax(dim=1)
            train_correct += (pred == batch.y).sum().item()
            train_total += batch.y.size(0)
        
        train_acc = train_correct / train_total
        
        # 验证
        val_acc = evaluate(model, val_loader)
        
        print(f"Epoch {epoch + 1}/{num_epochs}")
        print(f"Train Loss: {train_loss / len(train_loader):.4f}, Acc: {train_acc:.4f}")
        print(f"Val Acc: {val_acc:.4f}")
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'best_model.pth')

def evaluate(
    model: GraphPrompt,
    dataloader
) -> float:
    """评估模型"""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in dataloader:
            logits = model(
                batch.x,
                batch.edge_index,
                batch.batch
            )
            
            pred = logits.argmax(dim=1)
            correct += (pred == batch.y).sum().item()
            total += batch.y.size(0)
    
    return correct / total
```

## GraphPrompt 的应用场景

### 1. 图分类

**场景**：分类整个图

**示例**：
- 分子性质预测
- 社交网络分类
- 蛋白质结构分类

### 2. 节点分类

**场景**：分类图中的节点

**示例**：
- 社交网络中的用户分类
- 引用网络中的论文分类
- 知识图谱中的实体分类

### 3. 链路预测

**场景**：预测节点之间的连接

**示例**：
- 社交网络中的好友推荐
- 引用网络中的引文预测
- 知识图谱中的关系预测

### 4. 图生成

**场景**：生成新的图结构

**示例**：
- 分子生成
- 网络结构生成
- 知识图谱扩展

## GraphPrompt 的优势

### 1. 少样本学习

- **数据效率**：只需少量标注数据
- **快速适应**：快速适应新任务
- **跨任务泛化**：强跨任务泛化能力

### 2. 参数效率

- **冻结主干**：冻结预训练的图编码器
- **仅更新提示**：只更新提示参数
- **节省资源**：节省计算资源

### 3. 灵活性

- **任务适应**：易于适应不同任务
- **提示设计**：灵活的提示设计
- **模块化**：模块化设计

### 4. 性能提升

- **预训练利用**：利用预训练知识
- **提示增强**：提示增强表示
- **性能优越**：优于传统方法

## GraphPrompt 的局限性

### 1. 依赖预训练

- **挑战**：依赖高质量的预训练模型
- **解决方案**：改进预训练方法

### 2. 提示设计

- **挑战**：提示设计需要专业知识
- **解决方案**：自动化提示设计

### 3. 任务适应性

- **挑战**：某些任务适应性有限
- **解决方案**：改进提示融合机制

### 4. 计算成本

- **挑战**：图编码计算成本高
- **解决方案**：优化图编码效率

## 最佳实践

### 1. 预训练

- **大规模数据**：使用大规模图数据
- **多样化任务**：使用多样化任务
- **自监督学习**：使用自监督学习

### 2. 提示设计

- **任务相关**：设计任务相关的提示
- **多样化提示**：使用多样化提示
- **提示数量**：选择合适的提示数量

### 3. 任务适应

- **少样本学习**：使用少样本学习策略
- **快速适应**：实现快速适应机制
- **持续学习**：支持持续学习

### 4. 评估

- **多任务评估**：在多个任务上评估
- **跨任务泛化**：评估跨任务泛化能力
- **消融研究**：进行消融研究

## GraphPrompt 与其他技术的对比

| 特性 | GraphPrompt | 传统 GNN | 图提示学习 | GPT-4 |
|------|-------------|----------|-----------|-------|
| **输入类型** | 图结构 | 图结构 | 图结构 | 文本 |
| **任务适应** | 提示适应 | 微调 | 提示适应 | 提示适应 |
| **数据需求** | 少量 | 大量 | 少量 | 少量 |
| **计算成本** | 中 | 高 | 中 | 高 |
| **跨任务泛化** | 强 | 弱 | 强 | 强 |
| **可解释性** | 中 | 低 | 中 | 高 |

## 实际应用案例

### 案例 1：分子性质预测

**场景**：预测分子的性质

**GraphPrompt 应用：**
- 编码分子图结构
- 生成任务特定提示
- 预测分子性质
- 达到优异性能

### 案例 2：社交网络分析

**场景**：分析社交网络

**GraphPrompt 应用：**
- 编码社交网络结构
- 适应不同分析任务
- 识别社区结构
- 预测用户行为

### 案例 3：知识图谱推理

**场景**：在知识图谱上进行推理

**GraphPrompt 应用：**
- 编码知识图谱结构
- 适应推理任务
- 生成推理路径
- 完成知识补全

## 评估指标

### 1. 任务性能

- **准确率**：预测的准确率
- **F1 分数**：F1 分数
- **AUC-ROC**：AUC-ROC 分数

### 2. 泛化能力

- **跨任务泛化**：跨任务泛化能力
- **少样本性能**：少样本性能
- **零样本性能**：零样本性能

### 3. 效率指标

- **参数数量**：模型参数数量
- **训练时间**：训练时间
- **推理时间**：推理时间

## 相关技术

- **图神经网络（Graph Neural Networks）**：基础技术
- **提示学习（Prompt Learning）**：学习方法
- **预训练（Pre-training）**：预训练方法
- **迁移学习（Transfer Learning）**：学习方法
- **少样本学习（Few-Shot Learning）**：学习方法

## 参考资料

- Liu et al. (2023): "GraphPrompt: Unifying Pre-Training and Downstream Tasks for Graph Neural Networks"
- Prompt Engineering Guide: https://www.promptingguide.ai/zh/techniques/graph

## 练习

1. 实现一个简单的 GraphPrompt 模型
2. 使用 GraphPrompt 进行图分类任务
3. 实现 GraphPrompt 的少样本学习
4. 对比 GraphPrompt 和传统 GNN 的性能
5. 优化 GraphPrompt 的提示设计
