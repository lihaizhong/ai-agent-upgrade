# Embedding 技术与模型

Embedding（嵌入）是将高维离散数据（如文本、图像）映射到低维连续向量空间的技术。在 NLP 中，Embedding 使计算机能够以数学方式理解语义信息。

## 词嵌入（Word Embedding）

### One-Hot 编码

最早的文本表示方法：
- 词汇表中的每个词对应一个高维稀疏向量
- 向量维度等于词汇表大小
- 缺点：维度灾难，无法表达语义关系

### Word2Vec（2013）

Google 提出的经典词嵌入模型，基于分布式假设：相似的词出现在相似的上下文中。

**两种架构**：

- **CBOW（Continuous Bag of Words）**：用上下文预测中心词
- **Skip-gram**：用中心词预测上下文

**特点**：
- 将词映射到 100-300 维的密集向量
- 捕捉语义关系（如：king - man + woman ≈ queen）
- 训练速度快，适合大规模语料

**局限性**：
- 静态嵌入：每个词只有一个向量，无法处理一词多义
- 无法捕捉上下文信息

### GloVe（2014）

斯坦福提出的全局向量模型：
- 结合全局统计信息和局部上下文信息
- 基于词-词共现矩阵的分解
- 在类比任务上表现优异

### FastText（2016）

Facebook 提出的改进方案：
- 将词表示为 n-gram 字符组合的集合
- 能够处理未登录词（OOV）
- 对形态丰富的语言效果更好

## 上下文嵌入（Contextualized Embedding）

### ELMo（2018）

Embeddings from Language Models：
- 使用双向 LSTM 预训练
- 为每个词生成上下文相关的表示
- 不同层的表示捕捉不同层次的信息

### BERT 嵌入

BERT 的隐藏层输出可作为词的上下文表示：
- **[CLS] 标记**：用于句子级别的表示
- **最后一层隐藏状态**：用于词级别的表示
- **多层融合**：结合不同层的表示

### Sentence-BERT（2019）

专门用于句子嵌入的模型：
- 使用 Siamese 网络结构
- 通过对比学习优化句子表示
- 可直接用于语义相似度计算

## 现代 Embedding 模型

### OpenAI Embedding

- **text-embedding-ada-002**（2022）：1536 维，性能好，成本低
- **text-embedding-3-small**（2024）：更高性价比
- **text-embedding-3-large**（2024）：3072 维，最高性能

**特点**：
- 多语言支持
- 上下文长度 8192
- 通过 API 调用，无需本地部署

### BGE（BAAI General Embedding）

北京智源人工智能研究院开发的开源 Embedding 模型：

- **BGE-large-zh**：中文场景最优选择之一
- **BGE-m3**：多语言、多粒度、多任务
- **BGE-reranker**：重排序模型

**特点**：
- 开源免费，可本地部署
- 在 MTEB 榜单上表现优异
- 支持中英双语

### GTE（General Text Embedding）

阿里达摩院开发：
- **GTE-large-zh**：中文 Embedding 模型
- 基于多任务对比学习训练
- 在长文本检索上表现突出

### E5（EmbEddings from bidirEctional Encoder rEpresentations）

微软开发：
- **e5-large-v2**：通用 Embedding 模型
- **e5-mistral-7b-instruct**：基于 Mistral 的指令式 Embedding
- 在 MTEB 榜单上排名靠前

**特点**：
- 支持指令式嵌入（Instruction-based）
- 可以针对特定任务优化表示

### M3E（Moka Massive Mixed Embedding）

开源中文 Embedding 模型：
- 专门针对中文语料训练
- 支持多种粒度的嵌入（句子、段落、文档）
- 社区活跃，持续更新

### Cohere Embed

Cohere 提供的 Embedding API：
- **embed-english-v3**：英文专用
- **embed-multilingual-v3**：多语言版本
- 支持压缩和量化

### Voyage AI

专注于 Embedding 的创业公司：
- **voyage-2**：通用模型
- **voyage-code-2**：代码专用
- 在特定领域表现优异

## Embedding 模型的选择

### 考虑因素

1. **语言支持**：中文、英文、多语言
2. **向量维度**：影响存储和计算成本
3. **上下文长度**：能处理的最大文本长度
4. **性能指标**：在 MTEB 等基准测试上的表现
5. **部署方式**：API 调用或本地部署
6. **成本**：商业 API 费用或计算资源
7. **许可证**：开源协议是否允许商业使用

### 选择建议

**中文场景**：
- 追求性能：BGE-large-zh、GTE-large-zh
- 平衡成本：M3E、BGE-base-zh
- 快速原型：OpenAI text-embedding-3

**英文场景**：
- 追求性能：E5-mistral、voyage-2
- 平衡成本：E5-large-v2、BGE-large-en
- 快速原型：OpenAI text-embedding-3

**多语言场景**：
- BGE-m3、E5-multilingual、OpenAI embedding

**代码场景**：
- voyage-code-2、CodeBERT

## Embedding 的微调

### 为什么需要微调

通用 Embedding 模型在特定领域可能表现不佳：
- 领域术语理解不准确
- 领域内的语义关系与一般语料不同
- 需要针对特定任务优化

### 微调方法

**对比学习（Contrastive Learning）**：
- 准备正负样本对
- 拉近正样本的嵌入距离
- 推远负样本的嵌入距离
- 损失函数：InfoNCE、Triplet Loss

**指令微调（Instruction Tuning）**：
- 为不同任务添加指令前缀
- 如："检索：{query}"、"分类：{text}"
- 提高模型的任务适应性

### 数据准备

**正样本来源**：
- 用户点击日志（查询-文档对）
- 人工标注的相关性数据
- 文档内的自然关联（如标题-正文）

**负样本采样**：
- 随机采样（简单但质量低）
- 困难负样本（与正样本相似但不相关）
- 批量内负样本（同一批次内的其他样本）

## Embedding 的应用

### 语义搜索

将查询和文档都转换为 Embedding，通过向量相似度找到最相关的文档。

### 语义匹配

判断两个文本的语义相似度，用于：
- 重复内容检测
- 抄袭检测
- 语义去重

### 聚类与分类

利用 Embedding 的语义信息进行：
- 文档聚类
- 主题发现
- 文本分类

### 推荐系统

将用户和物品表示为 Embedding：
- 用户兴趣 Embedding
- 物品特征 Embedding
- 通过相似度进行推荐

### RAG 系统

RAG 的核心组件：
- 文档 Embedding 存储在向量数据库
- 查询 Embedding 用于检索
- 检索结果作为上下文增强生成

## 向量运算

Embedding 向量支持有趣的数学运算：

### 相似度计算

- **余弦相似度**：cos(θ) = (A·B) / (||A|| × ||B||)
- **欧氏距离**：d = √(Σ(Ai - Bi)²)
- **点积**：A·B = Σ(Ai × Bi)

### 向量运算

- **加法**：语义组合（如：king + woman）
- **减法**：语义差异（如：king - man）
- **平均**：句子或文档的平均表示

### 可视化

使用降维技术可视化 Embedding：
- **PCA**：主成分分析，线性降维
- **t-SNE**：非线性降维，保留局部结构
- **UMAP**：更高效的非线性降维

## 最佳实践

1. **预处理**：清洗文本，去除噪声
2. **批处理**：批量获取 Embedding，提高效率
3. **归一化**：对 Embedding 进行 L2 归一化，便于余弦相似度计算
4. **缓存**：缓存常见查询的 Embedding
5. **监控**：监控 Embedding 质量和分布漂移
6. **更新**：定期更新 Embedding 模型，跟进最新技术
