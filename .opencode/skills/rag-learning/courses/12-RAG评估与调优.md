# 12-RAG评估与调优

## 课程目标

- 掌握 RAG 评估指标
- 学会系统性调优方法
- 掌握 A/B 测试方法

---

## 1. RAG 评估体系

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG 评估维度                              │
├─────────────────────────────────────────────────────────────┤
                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │  检索质量   │  │  生成质量   │  │  系统性能   │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│   • MRR          • 答案相关性      • 响应延迟                │
│   • HitRate      • 答案完整性      • QPS                   │
│   • NDCG         • 幻觉程度        • 资源消耗                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 检索质量评估

### 2.1 核心指标

```python
from sklearn.metrics import ndcg_score
import numpy as np

def evaluate_retrieval(
    queries: list[str],
    relevant_docs: list[list[str]],
    vectorstore,
    k_values: list[int] = [1, 3, 5, 10]
) -> dict:
    """评估检索质量"""
    results = {}
    
    for k in k_values:
        hits = 0
        mrr_sum = 0
        
        for i, query in enumerate(queries):
            # 检索 Top-K
            retrieved = vectorstore.similarity_search(query, k=k)
            retrieved_ids = [doc.page_content for doc in retrieved]
            
            # Hit@K
            relevant = set(relevant_docs[i])
            if set(retrieved_ids) & relevant:
                hits += 1
            
            # MRR
            for rank, doc_id in enumerate(retrieved_ids, 1):
                if doc_id in relevant:
                    mrr_sum += 1 / rank
                    break
        
        results[f"hit@{k}"] = hits / len(queries)
        results[f"mrr@{k}"] = mrr_sum / len(queries)
    
    return results
```

### 2.2 NDCG 评估

```python
def evaluate_ndcg(
    queries: list[str],
    relevance_scores: list[list[float]],  # 0-1 相关性分数
    vectorstore,
    k: int = 10
) -> float:
    """NDCG@K 评估"""
    ndcg_scores = []
    
    for query, relevances in zip(queries, relevance_scores):
        retrieved = vectorstore.similarity_search(query, k=k)
        
        # 构建相关性向量
        relevance_vector = []
        for doc in retrieved:
            # 查找该文档的相关性分数
            doc_id = doc.page_content
            score = next((r for r in relevances if r["doc_id"] == doc_id), 0)
            relevance_vector.append(score)
        
        # 补齐到 k
        while len(relevance_vector) < k:
            relevance_vector.append(0)
        
        # 计算 NDCG
        actual_dcg = sum((2**rel - 1) / np.log2(idx + 2) 
                        for idx, rel in enumerate(relevance_vector))
        
        ideal_dcg = sum((2**rel - 1) / np.log2(idx + 2) 
                       for idx, rel in enumerate(sorted(relevance_vector, reverse=True)[:k]))
        
        ndcg_scores.append(actual_dcg / ideal_dcg if ideal_dcg > 0 else 0)
    
    return np.mean(ndcg_scores)
```

---

## 3. 生成质量评估

### 3.1 RAGAS 指标

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

def evaluate_generation(test_dataset, ragas_metrics=None):
    """使用 RAGAS 评估生成质量"""
    if ragas_metrics is None:
        ragas_metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    
    results = evaluate(
        dataset=test_dataset,
        metrics=ragas_metrics
    )
    
    return results
```

### 3.2 人工评估

```python
# 人工评估表
HUMAN_EVAL_TEMPLATE = """
Query: {query}
Retrieved Context: {context}
Generated Answer: {answer}

请评估：
1. 答案相关性 (1-5): {relevance}
2. 答案完整性 (1-5): {completeness}
3. 幻觉程度 (1-5，5=无幻觉): {hallucination}
4. 总体评分 (1-5): {overall}

建议：{feedback}
"""
```

---

## 4. 系统性能评估

```python
import time
from locust import TaskSet, HttpUser, task

class RAGLoadTest(TaskSet):
    @task
    def search_query(self):
        start = time.time()
        response = self.client.post("/api/search", json={
            "query": "测试查询",
            "top_k": 5
        })
        duration = time.time() - start
        
        # 记录
        print(f"Latency: {duration:.3f}s, Status: {response.status_code}")
```

---

## 5. A/B 测试框架

```python
class RAGABTest:
    """RAG A/B 测试"""
    
    def __init__(self, variant_a_config: dict, variant_b_config: dict):
        self.variants = {
            "A": self._build_rag(variant_a_config),
            "B": self._build_rag(variant_b_config)
        }
        self.results = {"A": [], "B": []}
    
    def _build_rag(self, config: dict):
        """根据配置构建 RAG"""
        return RAGSystem(
            embedding_model=config.get("embedding", "BAAI/bge-large-zh"),
            vector_db=config.get("vector_db", "chroma"),
            chunk_size=config.get("chunk_size", 500)
        )
    
    def run_test(self, queries: list[str], user_ids: list[str]):
        """运行测试"""
        for query, user_id in zip(queries, user_ids):
            variant = "A" if hash(user_id) % 2 == 0 else "B"
            result = self.variants[variant].query(query)
            self.results[variant].append({
                "query": query,
                "answer": result["answer"],
                "latency": result["latency"]
            })
    
    def analyze_results(self) -> dict:
        """分析结果"""
        analysis = {}
        for variant, results in self.results.items():
            latencies = [r["latency"] for r in results]
            analysis[variant] = {
                "count": len(results),
                "avg_latency": np.mean(latencies),
                "p50_latency": np.percentile(latencies, 50),
                "p95_latency": np.percentile(latencies, 95)
            }
        return analysis
```

---

## 6. 调优方法论

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG 调优流程                              │
├─────────────────────────────────────────────────────────────┤
                                                             │
│   1. 基准测试 ──▶ 2. 瓶颈分析 ──▶ 3. 优化实施 ──▶ 4. 验证  │
│         │              │              │              │       │
│         ▼              ▼              ▼              ▼       │
│   建立基线       定位问题       针对性优化     确认效果      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 调优清单

| 环节 | 检查项 | 优化方向 |
|------|--------|----------|
| 分块 | chunk_size 是否合适 | 200-1000 调整 |
| Embedding | 模型选择 | 对比多个模型 |
| 向量库 | 索引类型 | HNSW/IVF |
| 检索 | top_k 设置 | 3-10 调整 |
| Rerank | 是否需要 | 添加 Rerank |
| 生成 | Prompt 优化 | 调整模板 |

---

## 7. 总结

- 检索评估：Hit@K、MRR、NDCG
- 生成评估：RAGAS、人工评估
- 性能评估：延迟、QPS、资源
- 调优方法：基准 → 瓶颈 → 优化 → 验证