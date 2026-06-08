"""Chroma 向量存储 — 原生 API 操作"""

import os
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.embedder import get_embedder

_COLLECTION_NAME = "knowledge_base"


def _get_client() -> chromadb.PersistentClient:
    """获取 Chroma 持久化客户端"""
    persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIR)
    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(
        path=persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection() -> chromadb.Collection:
    """获取或创建知识库 Collection"""
    client = _get_client()
    embedder = get_embedder()
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        embedding_function=embedder,
    )


def add_document_to_chroma(
    chunks: list[str],
    metadata_list: list[dict],
) -> list[str]:
    """将文档分块向量化后存入 Chroma，返回 chunk IDs"""
    collection = get_collection()
    ids = [f"chunk_{meta['document_id']}_{meta['chunk_index']}"
           for meta in metadata_list]
    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadata_list,
    )
    return ids


def delete_document_from_chroma(document_id: int) -> None:
    """从 Chroma 中删除指定文档的所有分块"""
    collection = get_collection()
    try:
        results = collection.get(
            where={"document_id": document_id},
        )
        if results and results.get("ids"):
            collection.delete(ids=results["ids"])
    except Exception as e:
        # 可能没有匹配的记录
        pass


def search_similar(
    query: str,
    k: int | None = None,
) -> list[tuple[str, dict, float]]:
    """相似度检索，返回 [(content, metadata, distance), ...]

    注意：Chroma 返回 distance（距离），非相似度分数。
    距离越小表示越相似。
    """
    collection = get_collection()
    k = k or settings.RETRIEVAL_K
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    if not results or not results.get("documents") or not results["documents"][0]:
        return []

    docs = results["documents"][0]
    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
    dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

    return [(docs[i], metas[i], dists[i]) for i in range(len(docs))]
