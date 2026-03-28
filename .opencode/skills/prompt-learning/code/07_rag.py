"""
07 - 检索增强生成 (RAG)

RAG 通过检索外部知识来增强生成质量。
核心组件：
1. 文档分块 (Chunking)
2. 向量化 (Embedding)
3. 相似度检索 (Similarity Search)
4. 生成 (Generation)

注意：这是一个简化版的 RAG 框架。
生产环境建议使用 LangChain、LlamaIndex 等成熟框架。
"""

from utils import call_llm
import json


class SimpleRAG:
    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add_documents(self, docs: list):
        """添加文档"""
        self.documents.extend(docs)

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """检索相关文档（简化版：关键词匹配）"""
        query_words = set(query.lower().split())
        scored = []

        for i, doc in enumerate(self.documents):
            doc_words = set(doc.lower().split())
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scored.append((i, overlap, doc))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for _, _, doc in scored[:top_k]]

    def generate(self, query: str, use_retrieval: bool = True) -> dict:
        """生成回答"""
        if use_retrieval:
            relevant_docs = self.retrieve(query)
            context = "\n".join(relevant_docs)

            prompt = f"""基于以下参考资料回答问题。如果资料中没有相关信息，请说明。

参考资料：
{context}

问题：{query}

回答："""
        else:
            prompt = query

        result = call_llm(prompt)
        return result

    def answer(self, query: str) -> dict:
        """完整的 RAG 流程"""
        relevant_docs = self.retrieve(query)
        context = "\n".join(relevant_docs)

        prompt = f"""你是一个助手。请基于提供的参考资料回答问题。
如果资料中没有相关信息，请如实说明。

参考资料：
{context}

问题：{query}

请给出准确、详细的回答，并说明答案来自参考资料中的哪些部分。"""

        result = call_llm(prompt)

        return {
            "query": query,
            "retrieved_docs": relevant_docs,
            "answer": result["data"] if result["success"] else result["error"],
            "success": result["success"],
        }


def main():
    print("=" * 60)
    print("检索增强生成 (RAG) 示例")
    print("=" * 60)

    # 初始化 RAG
    rag = SimpleRAG()

    # 添加文档
    docs = [
        "人工智能（AI）是计算机科学的一个分支，致力于开发能够执行通常需要人类智能的任务的系统。",
        '机器学习是人工智能的一个子集，它使用统计技术使计算机系统能够从数据中"学习"，而不需要明确的编程。',
        "深度学习是机器学习的一个子集，它使用多层神经网络来分析各种因素的数据。",
        "自然语言处理（NLP）是人工智能的一个分支，专注于使计算机能够理解和生成人类语言。",
        "大语言模型（LLM）是一种基于深度学习的自然语言处理模型，能够理解和生成文本。",
        "GPT（生成式预训练变换器）是一种大语言模型，由OpenAI开发。",
        "Transformer是一种神经网络架构，是现代大语言模型的基础。",
    ]

    rag.add_documents(docs)

    # 测试查询
    queries = ["什么是人工智能？", "机器学习和深度学习有什么区别？", "GPT是什么？"]

    for query in queries:
        print(f"\n【查询】{query}")
        print("-" * 40)

        result = rag.answer(query)
        if result["success"]:
            print(f"检索到的文档：{len(result['retrieved_docs'])} 篇")
            print(f"\n回答：\n{result['answer']}")
        print()


if __name__ == "__main__":
    main()
