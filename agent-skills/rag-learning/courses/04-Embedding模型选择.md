# 04-Embedding模型选择

## 在平台中的位置

- 所属模块：`学习中心`
- 对应能力：`Embedding 选择`
- 建议衔接：
  - 学完后进入 `RAG Lab` 做 embedding 对比实验
  - 或进入实战中心的 embedding 步骤

## 使用提醒

- 这节课的模型列表应视为候选示例，不应被当成永久排行榜
- 如果用户要求“最新推荐”或“当前最佳”，应先核实官方资料
## 课程目标

- 理解 Embedding 的评估维度
- 掌握主流 Embedding 模型特点
- 学会根据场景选择合适的 Embedding 模型

## 1. Embedding 模型评估维度

选择 Embedding 模型时需要考虑以下维度：

### 1.1 性能指标

| 指标 | 说明 |
|------|------|
| **维度 (Dimension)** | 向量长度，通常 384-1536，维度越高精度越好但存储和检索更慢 |
| **MTEB 分数** | MassivText Embedding Benchmark，综合评估模型性能 |
| **检索精度** | 在具体任务上的检索效果 |

### 1.2 成本因素

| 因素 | 说明 |
|------|------|
| **API 费用** | OpenAI、Cohere 等商业模型的调用费用 |
| **部署成本** | 开源模型本地部署的 GPU 资源 |
| **维护成本** | 模型更新、迭代的人力成本 |

### 1.3 技术特性

| 特性 | 说明 |
|------|------|
| **语言支持** | 中文、英文、多语言 |
| **领域适配** | 通用模型 vs 领域微调模型 |
| **上下文长度** | 单次能处理的文本长度 |
| **推理速度** | 每秒能处理的请求数 |

---

## 2. 主流 Embedding 模型对比

### 2.1 OpenAI 系列

| 模型 | 维度 | MTEB | 费用 | 特点 |
|------|------|------|------|------|
| text-embedding-3-large | 3072 | 高 | $$ | 最佳效果，支持 8191 tokens |
| text-embedding-3-small | 1536 | 中高 | $ | 性价比高，比 ada-002 好 5 倍但便宜 50 倍 |
| ada-002 | 1536 | 中 | $ | 老牌模型，逐渐被取代 |

**推荐场景**：追求最佳效果、预算充足的场景

### 2.2 开源中文模型

| 模型 | 维度 | MTEB | 语言 | 特点 |
|------|------|------|------|------|
| BGE-large-zh | 1024 | 高 | 中文 | 通用中文最强，开源免费 |
| BGE-m3 | 1024 | 高 | 多语言 | 多语言支持，可处理 250+ 语言 |
| M3E | 1536 | 中 | 中文 | 中文免费，集成部署简单 |
| text2vec | 1024 | 中 | 中文 | 轻量级 |

**推荐场景**：中文场景、预算有限、需要本地部署

### 2.3 Cohere 系列

| 模型 | 维度 | MTEB | 特点 |
|------|------|------|------|
| embed-english-v3.0 | 1024 | 高 | 英文优化，多种尺寸 |
| embed-multilingual-v3.0 | 1024 | 高 | 多语言支持 |
| embed-english-light-v3.0 | 384 | 中 | 轻量快速 |

**推荐场景**：多语言场景、需要 Cohere Rerank 配合

### 2.4 其他模型

| 模型 | 特点 |
|------|------|
| Voyage AI | 企业级，高精度 |
| Mistral Embeddings | 开源，Mistral 模型 |
| Jina AI | 开源，中文支持 |

---

## 3. 模型选择决策树

```
开始选择 Embedding 模型
        │
        ▼
┌───────────────────┐
│  是否需要中文？    │
└───────────────────┘
        │
   ┌────┴────┐
   │ 是      │ 否
   ▼         ▼
┌─────────┐ ┌─────────────┐
│ 继续判断 │ │ 英文场景    │
└─────────┘ └─────────────┘
        │
        ▼
┌───────────────────┐
│  预算是否充足？    │
└───────────────────┘
        │
   ┌────┴────┐
   │ 是      │ 否
   ▼         ▼
┌─────────┐ ┌─────────────┐
│OpenAI   │ │ 开源模型    │
│3-large  │ │ BGE-large   │
└─────────┘ └─────────────┘
        │
        ▼
┌───────────────────┐
│  需要多语言？      │
└───────────────────┘
        │
   ┌────┴────┐
   │ 是      │ 否
   ▼         ▼
┌─────────┐ ┌─────────────┐
│BGE-m3   │ │ BGE-large-zh│
└─────────┘ └─────────────┘
```

---

## 4. 场景化推荐

### 场景一：中文文档问答

**需求特点**：
- 中文为主
- 追求精度
- 成本可控

**推荐选择**：
```
首选：BGE-large-zh
备选：text-embedding-3-small + 翻译
```

**选择理由**：
- BGE-large-zh 在中文 MTEB 上表现最佳
- 开源免费，成本最低
- 有多个开源版本可选

### 场景二：英文通用搜索

**需求特点**：
- 英文内容
- 高精度
- 云服务优先

**推荐选择**：
```
首选：text-embedding-3-large
备选：Cohere embed-english-v3.0
```

**选择理由**：
- OpenAI 生态成熟
- 3-large 效果最佳
- Cohere 有 Rerank 配合

### 场景三：多语言场景

**需求特点**：
- 多种语言混合
- 跨境业务
- 翻译成本高

**推荐选择**：
```
首选：BGE-m3
备选：Cohere embed-multilingual-v3.0
```

**选择理由**：
- BGE-m3 支持 250+ 语言
- 中文表现优异
- 多语言统一检索

### 场景四：实时对话系统

**需求特点**：
- 低延迟
- 高并发
- 响应快

**推荐选择**：
```
首选：text-embedding-3-small
备选：bge-small-zh
```

**选择理由**：
- 3-small 速度快
- 维度低（1536）
- 性能损失可接受

### 场景五：垂直领域（医疗/金融/法律）

**需求特点**：
- 专业术语
- 高准确性
- 领域知识

**推荐选择**：
```
首选：领域微调 BGE
备选：通用 BGE-large-zh + Prompt 优化
```

**选择理由**：
- 领域微调模型更专业
- 医疗、金融已有专门版本
- 通用模型 + 提示词也可接受

---

## 5. Embedding 效果评估方法

### 5.1 使用 MTEB 基准

MTEB（Massive Text Embedding Benchmark）涵盖 58 个数据集，8 个任务类型。

```python
from mteb import MTEB
from sentence_transformers import SentenceTransformer

# 加载模型
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

# 评估任务
evaluation = MTEB(task_names=[" retrieval"])
results = evaluation.run(model, output_folder="results/bge-large-zh")
```

### 5.2 实际数据测试

```python
from sklearn.metrics import ndcg_score
import numpy as np

def evaluate_retrieval(embeddings, queries, relevant_docs):
    """
    评估检索效果
    embeddings: 向量化模型
    queries: 测试问题列表
    relevant_docs: 每问题对应的相关文档
    """
    scores = []
    for query, relevant in zip(queries, relevant_docs):
        # 查询向量
        query_vec = embeddings.encode([query])
        
        # 检索结果
        results = vector_db.search(query_vec, top_k=10)
        
        # 计算 NDCG
        relevance = [1 if doc in relevant else 0 for doc in results]
        scores.append(ndcg_score([relevance], [[1]*len(relevant)]))
    
    return np.mean(scores)
```

---

## 6. 成本优化策略

### 6.1 维度缩减

OpenAI 的 Ada 和 3-small 支持自定义维度：

```python
from openai import OpenAI

client = OpenAI()

# 使用 256 维度，比默认 1536 小 6 倍
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Your text string",
    dimensions=256
)
```

### 6.2 批量处理

```python
# 批量向量化，减少 API 调用
batch_embeddings = client.embeddings.create(
    model="text-embedding-3-small",
    input=[
        "Text 1",
        "Text 2",
        "Text 3",
        # 最多 2048 条
    ]
)
```

### 6.3 缓存策略

```python
import hashlib

def get_embedding_cached(text, cache={}):
    """带缓存的向量化"""
    # 使用文本 hash 作为 key
    cache_key = hashlib.md5(text.encode()).hexdigest()
    
    if cache_key in cache:
        return cache[cache_key]
    
    embedding = embeddings.encode(text)
    cache[cache_key] = embedding
    return embedding
```

---

## 7. 总结

**选择 Embedding 模型的核心原则**：

| 原则 | 说明 |
|------|------|
| 中文优先 BGE | 开源免费效果好 |
| 追求效果选 OpenAI | 3-large 最佳 |
| 多语言选 BGE-m3 | 250+ 语言支持 |
| 实时性选小模型 | 3-small 或 bge-small |
| 领域专用微调 | 垂直领域效果最佳 |

**性价比推荐**：
- 最佳性价比：text-embedding-3-small（$0.02/1M tokens）
- 最佳中文：bge-large-zh（免费开源）
- 最佳多语言：bge-m3（免费开源）

---

## 课后问答

1. 选择 Embedding 模型需要考虑哪些维度？
2. BGE-large-zh 和 text-embedding-3-large 各自的优势是什么？
3. 什么场景下需要使用维度更低的 Embedding 模型？
4. 如何评估 Embedding 模型的实际效果？

---

## 下节预告

下一课我们将学习 **Rerank 模型选择**，了解两阶段检索如何提升精度，以及如何选择合适的 Rerank 模型。
