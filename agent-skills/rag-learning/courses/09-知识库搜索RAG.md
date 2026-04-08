# 09-知识库搜索RAG

## 课程目标

- 理解知识库搜索场景特点
- 掌握大规模文档处理方法
- 学会构建企业知识库搜索

---

## 1. 场景特点

| 特点 | 说明 |
|------|------|
| 海量文档 | 可能有百万级文档 |
| 精确匹配 | 需要找到准确答案 |
| 多种格式 | PDF/Word/HTML/PPT |
| 权限控制 | 不同用户看到不同内容 |
| 实时更新 | 知识库需要同步更新 |

---

## 2. 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                  企业知识库搜索架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │  数据采集 │───▶│  数据处理 │───▶│  向量化   │            │
│   └──────────┘    └──────────┘    └──────────┘            │
│         │               │               │                   │
│         ▼               ▼               ▼                   │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │  格式转换 │    │  分块   │    │  索引构建 │            │
│   └──────────┘    └──────────┘    └──────────┘            │
│                                              │                │
│                                              ▼                │
│   ┌──────────────────────────────────────────────────┐       │
│   │                   检索层                         │       │
│   │  语义检索 + 关键词检索 + 权限过滤 + Rerank      │       │
│   └──────────────────────────────────────────────────┘       │
│                                              │                │
│                                              ▼                │
│   ┌──────────────────────────────────────────────────┐       │
│   │                   应用层                         │       │
│   │  企业搜索 / 客服 / 文档问答                      │       │
│   └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 大规模文档处理

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus

class KnowledgeBaseProcessor:
    """知识库批量处理"""
    
    def __init__(self, vector_db_url: str = "http://localhost:19530"):
        self.loader = DirectoryLoader(
            "./knowledge_base",
            glob="**/*",
            show_progress=True
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-zh-v1.5"
        )
        self.vector_db_url = vector_db_url
    
    def process_all(self, batch_size: int = 100):
        """批量处理文档"""
        documents = self.loader.load()
        print(f"加载了 {len(documents)} 个文档")
        
        chunks = self.splitter.split_documents(documents)
        print(f"分块后 {len(chunks)} 个 chunks")
        
        # 批量写入向量库
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            self._write_to_vector_db(batch)
            print(f"已处理 {min(i+batch_size, len(chunks))}/{len(chunks)}")
    
    def _write_to_vector_db(self, chunks: list):
        """写入向量库"""
        vectorstore = Milvus.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            connection_args={"host": "localhost", "port": "19530"}
        )
        return vectorstore
```

---

## 4. 多租户权限控制

```python
class MultiTenantRAG:
    """多租户知识库"""
    
    def __init__(self):
        self.vectorstore = None
    
    def add_document(self, document: Document, tenant_id: str):
        """添加文档并标记租户"""
        document.metadata["tenant_id"] = tenant_id
        self.vectorstore.add_documents([document])
    
    def search(self, query: str, tenant_id: str, top_k: int = 5) -> list:
        """租户隔离搜索"""
        return self.vectorstore.similarity_search(
            query,
            k=top_k,
            filter={"tenant_id": tenant_id}  # 自动过滤其他租户数据
        )

# 使用示例
rag = MultiTenantRAG()
rag.vectorstore = existing_vectorstore

# 租户 A 的搜索
results_a = rag.search("如何报销", tenant_id="company_a")

# 租户 B 的搜索（只能看到自己的数据）
results_b = rag.search("如何报销", tenant_id="company_b")
```

---

## 5. 增量更新策略

```python
class IncrementalUpdater:
    """增量更新知识库"""
    
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.last_update_file = ".last_update"
    
    def get_last_update_time(self) -> datetime:
        """获取上次更新时间"""
        if os.path.exists(self.last_update_file):
            with open(self.last_update_file) as f:
                return datetime.fromisoformat(f.read())
        return datetime.min
    
    def update(self, docs_dir: str):
        """增量更新"""
        last_update = self.get_last_update_time()
        current_time = datetime.now()
        
        # 找出需要更新的文件
        files_to_update = []
        for root, _, files in os.walk(docs_dir):
            for f in files:
                path = os.path.join(root, f)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if mtime > last_update:
                    files_to_update.append(path)
        
        if not files_to_update:
            print("没有需要更新的文档")
            return
        
        # 加载并处理新文档
        for path in files_to_update:
            doc = loader.load(path)
            chunks = splitter.split_documents([doc])
            self.vectorstore.add_documents(chunks)
            print(f"已更新: {path}")
        
        # 记录更新时间
        with open(self.last_update_file, "w") as f:
            f.write(current_time.isoformat())
```

---

## 6. 企业搜索界面集成

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/search")
async def search(request: SearchRequest):
    """搜索 API"""
    results = vectorstore.similarity_search(
        request.query,
        k=request.top_k or 10,
        filter=request.filters
    )
    
    return {
        "results": [
            {
                "content": doc.page_content[:200],
                "source": doc.metadata.get("source"),
                "score": doc.metadata.get("score", 0)
            }
            for doc in results
        ],
        "total": len(results)
    }

@app.post("/api/index")
async def index_document(request: IndexRequest):
    """文档索引 API"""
    doc = Document(
        page_content=request.content,
        metadata=request.metadata or {}
    )
    vectorstore.add_documents([doc])
    return {"status": "indexed"}
```

---

## 7. 总结

- 海量文档需要批量处理
- 多租户通过 tenant_id 隔离
- 增量更新减少系统压力
- 权限控制是企業知識庫標配