# 07-文档问答RAG

## 课程目标

- 理解文档问答场景的特点
- 掌握文档问答 RAG 的技术选型
- 学会搭建一个完整的文档问答系统

## 1. 场景特点分析

### 1.1 文档问答的典型场景

| 场景 | 示例 | 特点 |
|------|------|------|
| 产品手册问答 | 用户询问"如何安装 XX" | 长文档、结构化 |
| 合同审查 | 询问"保密条款是什么" | 精确、法律术语 |
| 技术文档 | "如何配置 XX 参数" | 技术性强 |
| 论文阅读 | 总结论文核心观点 | 长文本理解 |
| 简历筛选 | 查找符合条件的人才 | 半结构化 |

### 1.2 核心挑战

```
┌─────────────────────────────────────────────────────────────┐
│                    文档问答核心挑战                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │  长文档处理  │  │  多格式支持  │  │ 精确信息提取 │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │  上下文丢失  │  │  专业术语   │  │  结构保持   │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**挑战详解**：

1. **长文档处理**：一篇 PDF 可能几十上百页，需要有效分块
2. **多格式支持**：PDF、Word、Markdown、HTML 格式各异
3. **精确信息提取**：用户可能问具体数字、日期、条款
4. **上下文丢失**：分块后丢失段落间关联
5. **专业术语**：法律、医疗、金融文档包含大量术语
6. **结构保持**：标题、目录、表格结构需要保留

---

## 2. 技术选型建议

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                  文档问答 RAG 架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │  文档加载 │───▶│  文档解析 │───▶│  内容切分 │            │
│   │  Loader  │    │  Parser  │    │  Chunker │            │
│   └──────────┘    └──────────┘    └──────────┘            │
│         │                               │                    │
│         ▼                               ▼                    │
│   ┌──────────┐                  ┌──────────┐              │
│   │  格式识别 │                  │  向量化   │              │
│   │          │                  │Embedding │              │
│   └──────────┘                  └──────────┘              │
│                                        │                    │
│                                        ▼                    │
│                                 ┌──────────┐              │
│                                 │ 向量存储  │              │
│                                 │  VectorDB │              │
│                                 └──────────┘              │
│                                        │                    │
│                                        ▼                    │
│   ┌──────────────────────────────────────────────────┐      │
│   │                    检索 + 生成                    │      │
│   └──────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 组件选型

| 组件 | 推荐选择 | 原因 |
|------|----------|------|
| **文档加载** | LangChain + Unstructured | 支持多种格式 |
| **分块策略** | 语义分块 / 文档结构分块 | 保留语义完整性 |
| **Embedding** | BGE-large-zh / text-embedding-3-small | 中文好 / 快速 |
| **向量数据库** | Chroma（开发）/ Qdrant（生产） | 轻量 / 高性能 |
| **Rerank** | BAAI/bge-reranker | 提升精度 |
| **生成模型** | GPT-4o-mini / Claude 3.5 | 成本与效果平衡 |

### 2.3 分块策略详解

**策略对比**：

| 策略 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| 固定大小 | 通用 | 简单快速 | 可能打断语义 |
| 语义分块 | 段落完整 | 保留语义 | 大小不均匀 |
| 文档结构 | 有标题结构 | 保留层级 | 依赖格式 |
| 递归分块 | 通用 | 灵活 | 复杂 |

**推荐配置**：

```python
# 语义分块（推荐文档问答）
from langchain.text_splitter import SemanticChunker
from langchain.embeddings import HuggingFaceEmbeddings

splitter = SemanticChunker(
    embeddings=HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh"),
    breakpoint_threshold_amount=0.8
)

# 固定大小分块（备选）
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # tokens
    chunk_overlap=50,    # 重叠保持上下文
    separators=["\n\n", "\n", "。", "！", "？", ""]
)
```

---

## 3. 实战搭建

### 3.1 环境准备

```bash
# 创建虚拟环境
uv venv rag-doc-qa
source rag-doc-qa/bin/activate

# 安装依赖
uv add langchain langchain-community langchain-openai \
    chromadb sentence-transformers pypdf python-docx \
    tiktoken
```

### 3.2 文档加载模块

```python
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader

class DocumentLoader:
    """文档加载器"""
    
    SUPPORTED_FORMATS = {
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.md': UnstructuredMarkdownLoader,
        '.txt': TextLoader,
    }
    
    def load(self, file_path: str) -> Document:
        ext = Path(file_path).suffix.lower()
        loader_class = self.SUPPORTED_FORMATS.get(ext)
        
        if not loader_class:
            raise ValueError(f"不支持的格式: {ext}")
        
        loader = loader_class(file_path)
        return loader.load()[0]
    
    def load_directory(self, dir_path: str) -> list[Document]:
        """批量加载目录下所有文档"""
        documents = []
        for file in Path(dir_path).rglob("*"):
            if file.suffix.lower() in self.SUPPORTED_FORMATS:
                try:
                    doc = self.load(str(file))
                    doc.metadata["source"] = str(file)
                    documents.append(doc)
                except Exception as e:
                    print(f"加载 {file} 失败: {e}")
        return documents
```

### 3.3 分块处理模块

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class TextChunker:
    """文本分块器"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ". ", " "]
        )
        return splitter.split_documents(documents)
    
    def split_with_metadata(self, text: str, metadata: dict) -> list[Document]:
        """带元数据的分块"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_text(text)
        return [
            Document(page_content=chunk, metadata=metadata)
            for chunk in chunks
        ]
```

### 3.4 向量存储模块

```python
import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

class VectorStore:
    """向量存储管理"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-zh-v1.5",
            model_kwargs={'device': 'cpu'}
        )
        self.client = chromadb.PersistentClient(path=persist_dir)
    
    def create_collection(self, name: str):
        """创建集合"""
        return self.client.create_collection(name=name)
    
    def add_documents(self, documents: list[Document], collection_name: str = "default"):
        """添加文档到向量库"""
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir,
            collection_name=collection_name
        )
        vectorstore.persist()
        return vectorstore
    
    def load_existing(self, collection_name: str = "default"):
        """加载已有向量库"""
        return Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
```

### 3.5 检索模块

```python
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.bm25 import BM25Retriever

class RAGRetriever:
    """RAG 检索器"""
    
    def __init__(self, vectorstore: Chroma, documents: list[Document]):
        self.vectorstore = vectorstore
        self.documents = documents
    
    def simple_retrieval(self, top_k: int = 5):
        """简单向量检索"""
        return self.vectorstore.as_retriever(
            search_kwargs={"k": top_k}
        )
    
    def hybrid_retrieval(self, top_k: int = 5, alpha: float = 0.5):
        """
        混合检索（向量 + BM25）
        alpha: 向量检索权重，1-alpha 为 BM25 权重
        """
        # 向量检索
        vector_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k * 2}
        )
        
        # BM25 检索
        bm25_retriever = BM25Retriever.from_documents(
            self.documents,
            preprocess_func=self._preprocess
        )
        bm25_retriever.k = top_k * 2
        
        # 合并
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[alpha, 1 - alpha]
        )
        return ensemble
    
    def retrieval_with_rerank(self, top_k: int = 5, rerank_top_k: int = 3):
        """带 Rerank 的检索"""
        base_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": top_k}
        )
        
        # 召回更多结果，rerank 后取 top_k
        return base_retriever  # 简化示例，实际用 Rerank 模型
    
    @staticmethod
    def _preprocess(text: str) -> list[str]:
        """BM25 预处理"""
        import re
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().split()
```

### 3.6 完整 RAG 链

```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class DocumentQA:
    """文档问答系统"""
    
    def __init__(
        self,
        vectorstore: Chroma,
        llm_model: str = "gpt-4o-mini"
    ):
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(model=llm_model, temperature=0)
        
        self.prompt = PromptTemplate(
            template="""基于以下参考内容回答用户问题。如果参考内容没有相关信息，请如实说明。
            
参考内容：
{context}

用户问题：{question}

请给出准确、完整的回答：""",
            input_variables=["context", "question"]
        )
    
    def create_chain(self):
        """创建问答链"""
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={
                "prompt": self.prompt
            },
            return_source_documents=True
        )
    
    def ask(self, question: str) -> dict:
        """提问"""
        chain = self.create_chain()
        result = chain({"query": question})
        
        return {
            "answer": result["result"],
            "sources": [
                {
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "unknown")
                }
                for doc in result.get("source_documents", [])
            ]
        }
```

### 3.7 使用示例

```python
# 初始化
loader = DocumentLoader()
documents = loader.load_directory("./docs/")

# 分块
chunker = TextChunker(chunk_size=500, chunk_overlap=50)
chunks = chunker.split(documents)

# 向量存储
vector_store = VectorStore(persist_dir="./chroma_db")
vector_store.add_documents(chunks, collection_name="doc-qa")

# 创建问答系统
qa = DocumentQA(vector_store)

# 提问
result = qa.ask("这份文档的主要内容是什么？")
print(f"回答: {result['answer']}")
print(f"来源: {result['sources']}")
```

---

## 4. 优化技巧

### 4.1 分块优化

```python
# 策略1：重叠分块，保持上下文
chunker = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,  # 50% overlap
    separators=["\n\n", "\n", "。", "！", "？"]
)

# 策略2：按标题分块，保持结构
from langchain.text_splitter import MarkdownTextSplitter

splitter = MarkdownTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# 策略3：句子级别分块（适合短问答）
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separators=["。", "！", "？", "\n", " "]
)
```

### 4.2 检索优化

```python
# MMR（最大边际相关）避免结果重复
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,           # 最终返回 5 个
        "fetch_k": 20,    # 初始检索 20 个
        "lambda_mult": 0.5  # 0=只管相关，1=只管多样
    }
)

# 元数据过滤
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {
            "category": "技术文档",
            "date": {"$gte": "2024-01-01"}
        }
    }
)
```

### 4.3 Prompt 优化

```python
# 精确回答 Prompt
exact_prompt = PromptTemplate(
    template="""基于参考内容，精确回答问题。

要求：
1. 如果参考内容包含确切答案，直接引用
2. 如果需要计算，用参考内容中的数据进行计算
3. 如果参考内容没有相关信息，明确说明"未找到"

参考内容：
{context}

问题：{question}

回答：""",
    input_variables=["context", "question"]
)

# 总结性回答 Prompt
summary_prompt = PromptTemplate(
    template="""阅读以下参考内容，用简洁的语言总结核心要点。

参考内容：
{context}

问题：{question}

总结：""",
    input_variables=["context", "question"]
)
```

---

## 5. 效果评估

### 5.1 检索评估

```python
from sklearn.metrics import precision_score, recall_score

def evaluate_retrieval(test_cases: list[dict]) -> dict:
    """评估检索效果"""
    results = []
    
    for case in test_cases:
        retrieved = qa.vectorstore.similarity_search(
            case["query"],
            k=case.get("k", 5)
        )
        
        # 计算命中情况
        relevant = set(case.get("relevant_docs", []))
        retrieved_set = set([doc.page_content for doc in retrieved])
        
        hit = len(relevant & retrieved_set) > 0
        
        results.append({
            "query": case["query"],
            "hit": hit,
            "precision": len(relevant & retrieved_set) / len(retrieved_set) if retrieved_set else 0
        })
    
    return {
        "hit_rate": sum(r["hit"] for r in results) / len(results),
        "avg_precision": sum(r["precision"] for r in results) / len(results)
    }
```

### 5.2 生成评估

```python
def evaluate_generation(test_cases: list[dict]) -> dict:
    """评估生成质量"""
    scores = []
    
    for case in test_cases:
        result = qa.ask(case["query"])
        
        # 评估维度
        relevance = evaluate_relevance(result["answer"], case["expected"])
        completeness = evaluate_completeness(result["answer"], case.get("required_points", []))
        
        scores.append({
            "relevance": relevance,
            "completeness": completeness
        })
    
    return {
        "avg_relevance": sum(s["relevance"] for s in scores) / len(scores),
        "avg_completeness": sum(s["completeness"] for s in scores) / len(scores)
    }
```

---

## 6. 总结

**文档问答 RAG 关键要点**：

| 要点 | 建议 |
|------|------|
| 分块策略 | 语义分块或 500 tokens 重叠 50 |
| Embedding | BGE-large-zh（中文）或 text-embedding-3-small（快） |
| 向量库 | Chroma（开发）/ Qdrant（生产） |
| Rerank | BAAI/bge-reranker 提升精度 |
| 生成 | GPT-4o-mini / Claude 3.5 |
| 检索优化 | MMR + 元数据过滤 |

**完整流程**：
1. 文档加载 → 2. 分块处理 → 3. 向量化 → 4. 存储 → 5. 检索 → 6. Rerank → 7. 生成

---

## 课后练习

1. 使用提供的示例文档，搭建一个完整的文档问答系统
2. 尝试不同的分块策略，比较效果差异
3. 添加 Rerank 模块，观察精度提升
4. 准备测试集，评估系统效果

---

## 下节预告

下一课我们将学习 **客服机器人 RAG**，了解如何构建支持多轮对话的客服系统。