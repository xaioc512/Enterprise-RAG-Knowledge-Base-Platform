"""本地嵌入模型封装 — 使用 Chroma 内置 ONNX 模型（all-MiniLM-L6-v2）"""

from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions

_embedder = None


def get_embedder() -> EmbeddingFunction:
    """获取本地嵌入模型实例（单例）"""
    global _embedder
    if _embedder is None:
        _embedder = embedding_functions.DefaultEmbeddingFunction()
    return _embedder


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量文本向量化"""
    embedder = get_embedder()
    return embedder(texts)


def embed_query(text: str) -> list[float]:
    """查询文本向量化"""
    embedder = get_embedder()
    return embedder([text])[0]
