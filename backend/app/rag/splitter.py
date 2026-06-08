"""文本分块器 — 基于 LangChain RecursiveCharacterTextSplitter"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def create_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> RecursiveCharacterTextSplitter:
    """创建文本分块器"""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", ".", "；", ";", " ", ""],
        length_function=len,
    )


def split_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """将文本分块，返回字符串列表"""
    splitter = create_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_text(text)
    return chunks
