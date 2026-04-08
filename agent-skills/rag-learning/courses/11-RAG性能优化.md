# 11-RAG性能优化

## 课程目标

- 掌握 RAG 各环节性能优化方法
- 学会诊断和解决性能瓶颈
- 掌握成本优化技巧

---

## 1. 性能优化全景图

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG 性能瓶颈                              │
├─────────────────────────────────────────────────────────────┤
                                                             │
│   文档加载 ──▶ 分块 ──▶ Embedding ──▶ 存储 ──▶ 检索 ──▶ 生成  │
│      │                                      │              │
│      ▼                                      ▼              │
│   加载慢      分块大    Embedding慢    索引慢    查询慢    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Embedding 优化

### 2.1 模型选择

```python
# 快速 Embedding
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 或开源快速模型
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
```

### 2.2 批量处理

```python
# 批量向量化
batch_embeddings = embeddings.embed_documents(texts)  # 一次处理多文本
```

### 2.3 缓存

```python
import hashlib

def cached_embed(text: str, cache: dict) -> list:
    key = hashlib.md5(text.encode()).digest()
    if key in cache:
        return cache[key]
    result = embeddings.embed(text)
    cache[key] = result
    return result
```

---

## 3. 检索优化

### 3.1 索引优化

```python
# Qdrant 优化索引
client.create_collection(
    collection_name="optimized",
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE,
        hnsw_config={
            "m": 16,        # 增大 m 提高精度
            "ef_construct": 128  # 增大提高精度
        }
    )
)
```

### 3.2 查询优化

```python
# 限制返回数量
results = vectorstore.similarity_search(query, k=5)  # 不要贪多

# 使用 ANN 而非精确搜索
retriever = vectorstore.as_retriever(
    search_type="similarity"  # ANN 近似搜索
)
```

---

## 4. 生成优化

### 4.1 流式输出

```python
# 流式生成减少等待感
from langchain.callbacks import StreamingStdOutCallbackHandler

chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    ),
    retriever=retriever
)
```

### 4.2 并行处理

```python
import asyncio

async def parallel_retrieve_and_generate(query: str):
    # 检索和生成并行
    retrieval_task = asyncio.create_task(retriever.aget_relevant_documents(query))
    generation_task = asyncio.create_task(llm.agenerate(draft_answer))
    
    docs = await retrieval_task
    answer = await generation_task
    
    return finalize(answer, docs)
```

---

## 5. 成本优化

| 优化项 | 方法 | 节省 |
|--------|------|------|
| Embedding 模型 | 用 3-small 而非 3-large | 50% |
| 向量维度 | 缩减到 256-512 | 60% |
| Query 缓存 | 相同 query 缓存 | 30% |
| LLM 降级 | 高峰用 4o-mini | 80% |
| 批量处理 | 积累后批量 | 20% |

---

## 6. 总结

- Embedding：选小模型 + 批量 + 缓存
- 检索：优化索引 + 限制 k 值
- 生成：流式输出 + 并行处理
- 成本：模型降级 + 缓存复用