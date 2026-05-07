from pathlib import Path
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

# 加载轻量级中文 embedding 模型（首次运行会自动下载）
# 如果不需要中文支持，可换成 "all-MiniLM-L6-v2"
_EMBEDDER = SentenceTransformer("BAAI/bge-small-zh-v1.5")

all_chunks: List[str] = []

# 缓存 chunk 对应的 embedding（shape: [num_chunks, embedding_dim]）
_chunk_embeddings: np.ndarray = np.array([])


# 1. 知识库文档
def load_documents(kb_dir: str = "knowledge_base") -> List[str]:
    """加载 knowledge_base 目录下所有 .md 文件内容。"""
    kb_path = Path(__file__).parent / kb_dir
    docs = []
    for md_file in sorted(kb_path.glob("*.md")):
        docs.append(md_file.read_text(encoding="utf-8"))
    return docs


# 2. 实现分块
def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """按字符长度分块，相邻块之间保留 overlap 重叠。"""
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = end - overlap
    return chunks


# 3. 获取 embedding
def get_embedding(text: str) -> np.ndarray:
    """使用 sentence-transformers 获取文本的向量表示。"""
    return _EMBEDDER.encode(text, normalize_embeddings=True)


def get_embeddings_batch(texts: List[str]) -> np.ndarray:
    """批量获取 embedding，效率更高。"""
    return _EMBEDDER.encode(texts, normalize_embeddings=True)


# 4. 余弦相似度检索
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个向量的余弦相似度（假设向量已归一化）。"""
    return float(np.dot(a, b))


def retrieve(query: str, chunks: List[str], top_k: int = 3) -> List[str]:
    """检索与查询最相关的 top_k 个 chunk。"""
    if not chunks or _chunk_embeddings.size == 0:
        return []

    query_embed = get_embedding(query)
    # 计算查询与所有 chunk 的相似度
    similarities = np.dot(_chunk_embeddings, query_embed)
    # 取相似度最高的 top_k 个索引
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [chunks[i] for i in top_indices]


# 5. 组装 prompt
def build_prompt(query: str, relevant_chunks: List[str]) -> str:
    context = "\n\n".join(
        f"[文档片段 {i + 1}]\n{chunk}" for i, chunk in enumerate(relevant_chunks)
    )
    prompt = f"""基于以下参考资料回答问题：

{context}

---
问题：{query}

请根据以上资料回答，如果资料不足以回答问题，请明确说明。"""
    return prompt


def build_index(docs: List[str], chunk_size: int = 500, overlap: int = 100):
    """构建知识库索引：分块 + 计算 embedding。"""
    global all_chunks, _chunk_embeddings

    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_text(doc, chunk_size=chunk_size, overlap=overlap))

    print(f"共加载 {len(docs)} 篇文档，切分为 {len(all_chunks)} 个片段")

    if all_chunks:
        _chunk_embeddings = get_embeddings_batch(all_chunks)
        print(f"Embedding 维度：{_chunk_embeddings.shape[1]}")


if __name__ == "__main__":
    # 加载知识库文档
    documents = load_documents()

    # 构建索引
    build_index(documents)

    # 测试查询
    query = "RAG 系统是什么？"
    results = retrieve(query, all_chunks, top_k=3)
    print("\n" + "=" * 60)
    print("检索结果：")
    for i, chunk in enumerate(results, 1):
        preview = chunk.replace("\n", " ")[:120]
        print(f"\n[{i}] {preview}...")

    print("\n" + "=" * 60)
    print("组装后的 Prompt：")
    print(build_prompt(query, results))
