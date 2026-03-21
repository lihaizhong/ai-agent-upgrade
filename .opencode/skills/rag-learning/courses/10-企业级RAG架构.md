# 10-企业级RAG架构

## 课程目标

- 理解企业级 RAG 架构设计原则
- 掌握高可用架构设计
- 学会构建可扩展的 RAG 系统

---

## 1. 企业级 RAG 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    企业级 RAG 架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                   接入层                             │  │
│   │  负载均衡 / API 网关 / 认证鉴权                      │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                 │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                   应用层                            │  │
│   │  问答服务 / 搜索服务 / 管理后台                      │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                 │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                   服务层                            │  │
│   │  RAG Pipeline / 缓存服务 / 任务调度                  │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                 │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                   数据层                            │  │
│   │  向量库 / 关系库 / 文件存储 / 缓存                   │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 核心组件设计

### 2.1 负载均衡

```python
# 多 LLM 实例负载均衡
from llama_index.llms import ChatGPT

class LoadBalancedLLM:
    def __init__(self, endpoints: list[str]):
        self.endpoints = endpoints
        self.current = 0
    
    def chat(self, messages, model: str = "gpt-4o"):
        endpoint = self.endpoints[self.current]
        self.current = (self.current + 1) % len(self.endpoints)
        return self._call_api(endpoint, messages, model)
```

### 2.2 缓存策略

```python
import redis
import hashlib

class RAGCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_cached_response(self, query: str, top_k: int) -> list:
        cache_key = self._make_key(query, top_k)
        return self.redis.get(cache_key)
    
    def cache_response(self, query: str, top_k: int, results: list):
        cache_key = self._make_key(query, top_k)
        self.redis.setex(cache_key, 3600, str(results))  # 1小时过期
    
    def _make_key(self, query: str, top_k: int) -> str:
        return hashlib.md5(f"{query}:{top_k}".encode()).hexdigest()
```

### 2.3 异步处理

```python
from celery import Celery

celery_app = Celery("rag_tasks")

@celery_app.task
def index_document_task(file_path: str):
    """异步文档索引"""
    doc = load_document(file_path)
    chunks = split_documents(doc)
    vectorstore.add_documents(chunks)
    return {"status": "indexed", "file": file_path}

# 触发异步任务
task = index_document_task.delay("/path/to/doc.pdf")
```

---

## 3. 高可用设计

### 3.1 多副本部署

```yaml
# docker-compose.yml 示例
services:
  qdrant:
    image: qdrant/qdrant
    replicas: 3
    
  api:
    build: ./api
    replicas: 3
    depends_on:
      - qdrant
```

### 3.2 熔断降级

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def call_llm_with_fallback(query: str) -> str:
    try:
        return llm.chat(query)
    except LLMOverloadError:
        return cached_answer(query)  # 降级返回缓存
```

---

## 4. 监控与告警

```python
from prometheus_client import Counter, Histogram

# 监控指标
query_count = Counter("rag_queries_total", "Total RAG queries")
query_latency = Histogram("rag_query_duration_seconds", "Query latency")
retrieval_precision = Histogram("rag_retrieval_precision", "Retrieval precision")

# 使用
@query_latency.time()
def process_query(query: str):
    query_count.inc()
    # 处理查询
```

---

## 5. 成本控制

| 策略 | 方法 | 效果 |
|------|------|------|
| 模型降级 | 高峰用小模型 | 成本-50% |
| 缓存复用 | 相同问题缓存 | 成本-30% |
| 批量处理 | 积累后批量 | 成本-20% |
| 索引压缩 | 减小向量维度 | 存储-60% |

---

## 6. 总结

- 企业级需要完整的基础设施
- 缓存、异步、监控是标配
- 高可用需要多副本部署
- 成本控制不可忽视