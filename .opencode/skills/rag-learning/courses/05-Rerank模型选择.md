# 05-Rerank模型选择

## 课程目标

- 理解 Rerank 的作用和原理
- 掌握主流 Rerank 模型
- 学会在 RAG 中使用 Rerank

---

## 1. 什么是 Rerank

Rerank（重排）是在向量检索后，对结果进行二次排序的技术。

**两阶段检索**：
```
用户查询 → 向量检索（快速召回 Top-K）→ Rerank（精排）→ 最终结果
```

---

## 2. Rerank vs 直接检索

| 对比项 | 直接向量检索 | 向量检索 + Rerank |
|--------|--------------|-------------------|
| 速度 | 快 | 稍慢 |
| 精度 | 中等 | 高 |
| 成本 | 低 | 较高 |
| 适用场景 | 简单场景 | 精度要求高 |

---

## 3. 主流 Rerank 模型

| 模型 | 类型 | 特点 |
|------|------|------|
| **Cohere Rerank** | 云服务 | 效果好、使用简单 |
| **BAAI/bge-reranker** | 开源 | 中文优化、可本地部署 |
| **Cross-Encoder** | 本地 | 灵活、可微调 |

---

## 4. Cohere Rerank 使用

```python
from cohere import Client

co = Client(api_key="your-api-key")

response = co.rerank(
    model="rerank-multilingual-v3.0",
    query="用户问题",
    documents=["文档1", "文档2", "文档3"],
    top_n=3
)

for result in response.results:
    print(result.document.text, result.relevance_score)
```

---

## 5. 开源 Rerank 使用

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("BAAI/bge-reranker-base")

# 对 Query-Document 对打分
scores = model.predict([
    ("用户问题", "文档1"),
    ("用户问题", "文档2"),
    ("用户问题", "文档3")
])

# 按分数排序
ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
```

---

## 6. LangChain 集成

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.embeddings import CohereRerank

compressor = CohereRerank(cohere_api_key="your-key", top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_retriever=vectorstore.as_retriever(),
    compressors=[compressor]
)
```

---

## 7. 何时需要 Rerank

**需要 Rerank**：
- 向量检索精度不够
- 文档语义复杂
- 精度要求高

**不需要 Rerank**：
- 数据量小
- 实时性要求极高
- 成本敏感

---

## 8. 总结

- Rerank 是两阶段检索的关键
- Cohere Rerank：效果最佳
- BAAI/bge-reranker：开源中文首选
- 精度与速度的权衡