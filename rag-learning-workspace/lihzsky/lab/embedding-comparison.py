#!/usr/bin/env python3
"""
Embedding 对比实验脚本
课程 04 实践：比较两个 embedding 模型在法律合同语料上的检索表现

依赖安装:
    uv add sentence-transformers numpy scikit-learn

运行:
    uv run python rag-learning-workspace/lihzsky/lab/embedding-comparison.py
"""

from __future__ import annotations

import time
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============ 1. 示例语料：法律合同条款 ============
CORPUS = [
    {
        "id": "clause_1",
        "text": "第七条 违约责任。任何一方违反本合同约定，应向守约方支付违约金。违约金数额为合同总金额的百分之二十。如违约金不足以弥补损失的，守约方有权要求赔偿实际损失。",
    },
    {
        "id": "clause_2",
        "text": "第八条 合同解除。在下列情形下，任何一方可以书面通知对方解除本合同：（一）因不可抗力致使不能实现合同目的；（二）一方迟延履行主要债务，经催告后在合理期限内仍未履行；（三）一方明确表示或者以自己的行为表明不履行主要债务。",
    },
    {
        "id": "clause_3",
        "text": "第九条 保密义务。双方对在合同履行过程中知悉的对方商业秘密、技术秘密及其他保密信息负有保密义务。未经对方书面同意，任何一方不得向第三方披露。保密期限自本合同生效之日起至合同终止后三年。",
    },
    {
        "id": "clause_4",
        "text": "第十条 知识产权。合同履行过程中产生的所有知识产权归甲方所有。乙方在履行合同过程中使用甲方提供的资料、数据和信息，仅可用于履行本合同之目的，不得用于其他任何用途。",
    },
    {
        "id": "clause_5",
        "text": "第十一条 争议解决。因本合同引起的或与本合同有关的任何争议，双方应首先通过友好协商解决。协商不成的，任何一方均可向甲方所在地有管辖权的人民法院提起诉讼。",
    },
]


# ============ 2. 测试查询 ============
QUERIES = [
    "违约责任条款在哪里？",
    "什么情况下可以解除合同？",
    "保密义务的范围和期限是什么？",
    "知识产权归谁所有？",
    "发生争议怎么解决？",
]


# 查询与预期条款的映射（用于自动评估）
EXPECTED_MAPPING = {
    0: ["clause_1"],  # 违约责任
    1: ["clause_2"],  # 合同解除
    2: ["clause_3"],  # 保密义务
    3: ["clause_4"],  # 知识产权
    4: ["clause_5"],  # 争议解决
}


# ============ 3. 模型配置 ============
MODELS = {
    "bge-m3": "BAAI/bge-m3",
    "minilm-l6": "all-MiniLM-L6-v2",
}


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """对文本列表进行 embedding，启用归一化。"""
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def retrieve(
    query_embedding: np.ndarray,
    doc_embeddings: np.ndarray,
    corpus: list[dict],
    top_k: int = 5,
) -> list[tuple[str, float]]:
    """基于余弦相似度检索 Top-K 文档。"""
    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [(corpus[i]["id"], float(similarities[i])) for i in top_indices]


def calculate_hit_rate(results: list[tuple[str, float]], query_index: int) -> float:
    """计算单次查询是否命中预期条款。"""
    expected = EXPECTED_MAPPING.get(query_index, [])
    retrieved_ids = [r[0] for r in results]
    return 1.0 if any(exp in retrieved_ids for exp in expected) else 0.0


def run_experiment(model_name: str, model_path: str) -> dict:
    """运行单个模型的完整实验。"""
    print(f"\n{'=' * 60}")
    print(f"正在测试模型: {model_name} ({model_path})")
    print(f"{'=' * 60}")

    # 加载模型
    load_start = time.time()
    model = SentenceTransformer(model_path)
    load_time = time.time() - load_start
    print(f"模型加载时间: {load_time:.2f}s")

    # Embedding 语料
    embed_start = time.time()
    doc_texts = [doc["text"] for doc in CORPUS]
    doc_embeddings = embed_texts(model, doc_texts)
    embed_time = time.time() - embed_start
    print(f"语料 embedding 时间: {embed_time:.2f}s (共 {len(CORPUS)} 条)")

    # 执行查询
    results_all = []
    total_query_time = 0.0

    for i, query in enumerate(QUERIES):
        query_start = time.time()
        query_embedding = embed_texts(model, [query])[0]
        results = retrieve(query_embedding, doc_embeddings, CORPUS, top_k=5)
        query_time = time.time() - query_start
        total_query_time += query_time

        hit = calculate_hit_rate(results, i)
        results_all.append({
            "query": query,
            "results": results,
            "hit": hit,
            "time": query_time,
        })

        print(f"\n查询 {i + 1}: {query}")
        print(f"  延迟: {query_time * 1000:.1f}ms")
        print("  Top-5 结果:")
        for doc_id, score in results:
            print(f"    {doc_id}: {score:.4f}")
        print(f"  是否命中: {'命中' if hit else '未命中'}")

    # 汇总指标
    hit_rate = sum(r["hit"] for r in results_all) / len(results_all)
    avg_latency = total_query_time / len(results_all)

    print(f"\n{'-' * 60}")
    print(f"模型 {model_name} 汇总:")
    print(f"  Hit Rate@5: {hit_rate * 100:.1f}%")
    print(f"  平均查询延迟: {avg_latency * 1000:.1f}ms")
    print(f"  模型加载时间: {load_time:.2f}s")

    return {
        "model": model_name,
        "model_path": model_path,
        "hit_rate": hit_rate,
        "avg_latency_ms": avg_latency * 1000,
        "load_time_s": load_time,
        "details": results_all,
    }


def save_results(all_results: list[dict]) -> None:
    """将实验结果保存到 workspace。"""
    output_dir = Path(__file__).parent
    output_file = output_dir / "embedding-experiment-result.json"

    summary = {
        "experiment": "embedding-comparison",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "corpus_size": len(CORPUS),
        "query_count": len(QUERIES),
        "models_tested": list(MODELS.keys()),
        "results": all_results,
    }

    output_file.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n实验结果已保存: {output_file}")


def print_comparison_table(results: list[dict]) -> None:
    """打印对比表格。"""
    print("\n" + "=" * 60)
    print("对比结果汇总")
    print("=" * 60)
    print(f"{'模型':<18} {'Hit Rate@5':<12} {'平均延迟':<12} {'加载时间':<12}")
    print("-" * 60)
    for r in results:
        print(
            f"{r['model']:<18} "
            f"{r['hit_rate'] * 100:>10.1f}% "
            f"{r['avg_latency_ms']:>10.1f}ms "
            f"{r['load_time_s']:>10.2f}s"
        )


def print_conclusion(results: list[dict]) -> None:
    """基于结果给出建议。"""
    print("\n" + "=" * 60)
    print("实验结论与建议")
    print("=" * 60)

    best_hit = max(results, key=lambda x: x["hit_rate"])
    best_latency = min(results, key=lambda x: x["avg_latency_ms"])

    print(f"召回最佳: {best_hit['model']} (Hit Rate@5: {best_hit['hit_rate'] * 100:.1f}%)")
    print(f"延迟最低: {best_latency['model']} (平均延迟: {best_latency['avg_latency_ms']:.1f}ms)")

    print("\n建议:")
    if best_hit["model"] == best_latency["model"]:
        print(f"  {best_hit['model']} 在召回和延迟上均表现最佳，建议作为默认选择。")
    else:
        print(f"  如果优先召回精度，选 {best_hit['model']}")
        print(f"  如果优先响应速度，选 {best_latency['model']}")
        print("  实际部署时需根据业务场景权衡。")

    print("\n下一步:")
    print("  1. 替换为真实语料重新运行")
    print("  2. 调整 chunking 策略后再次对比")
    print("  3. 进入课程 06 学习检索策略优化")


def main() -> None:
    print("RAG Learning - Embedding 对比实验")
    print("=" * 60)
    print(f"语料: {len(CORPUS)} 个合同条款")
    print(f"查询: {len(QUERIES)} 个测试问题")
    print(f"对比模型: {', '.join(MODELS.keys())}")
    print("注意: 首次运行会自动下载模型，可能需要几分钟")

    # 运行两组实验
    all_results = []
    for name, path in MODELS.items():
        result = run_experiment(name, path)
        all_results.append(result)

    # 输出结果
    print_comparison_table(all_results)
    print_conclusion(all_results)
    save_results(all_results)


if __name__ == "__main__":
    main()
