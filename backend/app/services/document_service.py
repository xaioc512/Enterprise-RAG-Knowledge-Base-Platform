"""文档管理服务 — 上传、解析、分块、向量化"""

import os
import hashlib
import uuid
from pathlib import Path
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from loguru import logger

from app.config import settings
from app.models.document import Document, DocumentChunk
from app.rag.loader import load_document, DocumentLoadError
from app.rag.splitter import split_text
from app.rag.retriever import add_document_to_chroma, delete_document_from_chroma
from app.rag.embedder import embed_texts, embed_query


async def save_upload_file(upload_file: UploadFile) -> tuple[str, str]:
    """保存上传文件到 uploads/ 目录，返回 (file_path, stored_filename)"""
    # 生成唯一文件名避免冲突
    ext = Path(upload_file.filename).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / stored_name

    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"File saved: {file_path} ({len(content)} bytes)")
    return str(file_path.absolute()), stored_name


async def process_document(
    document_id: int,
    file_path: str,
    file_type: str,
    db: AsyncSession,
) -> None:
    """
    处理文档：加载 → 分块 → 向量化 → 存储 → 更新状态

    此函数可通过 Celery 异步调用，也可在 API 中直接 await。
    """
    try:
        # 1. 加载文档文本
        logger.info(f"Processing document {document_id} ({file_type}): {file_path}")
        text = load_document(file_path, file_type)

        # 2. 文本分块
        chunks = split_text(text)
        logger.info(f"Document {document_id}: {len(chunks)} chunks created")

        if not chunks:
            raise ValueError("文档分块结果为空")

        # 3. 保存分块到 MySQL
        chunk_hashes = []
        for i, chunk_text in enumerate(chunks):
            chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
            chunk_hashes.append(chunk_hash)
            doc_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=chunk_text,
                chunk_hash=chunk_hash,
            )
            db.add(doc_chunk)

        await db.flush()

        # 4. 准备 Chroma 元数据
        # 获取文档信息
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one()

        metadata_list = []
        for i, chunk_text in enumerate(chunks):
            metadata_list.append({
                "document_id": document_id,
                "document_title": doc.title,
                "chunk_index": i,
                "category_id": doc.category_id or 0,
                "source_text_preview": chunk_text[:200],
            })

        # 5. 向量化并存入 Chroma
        ids = add_document_to_chroma(chunks, metadata_list)
        logger.info(f"Document {document_id}: {len(ids)} vectors stored in Chroma")

        # 6. 更新文档状态
        doc.status = "done"
        doc.chunk_count = len(chunks)
        await db.flush()

        logger.info(f"Document {document_id} processed successfully")

    except Exception as e:
        logger.error(f"Document {document_id} processing failed: {e}")
        # 更新文档状态为错误
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if doc:
            doc.status = "error"
            doc.error_message = str(e)
            await db.flush()
        raise


async def reprocess_document(document_id: int, db: AsyncSession) -> None:
    """重新处理文档（删除旧数据后重新解析）"""
    # 删除旧的 Chroma 数据
    delete_document_from_chroma(document_id)

    # 删除旧的分块记录
    result = await db.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )
    old_chunks = result.scalars().all()
    for chunk in old_chunks:
        await db.delete(chunk)
    await db.flush()

    # 获取文档信息
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one()
    doc.status = "processing"
    doc.error_message = None
    await db.flush()

    # 重新处理
    await process_document(document_id, doc.file_path, doc.file_type, db)


def detect_file_type(filename: str) -> str:
    """根据文件扩展名检测文件类型"""
    ext = Path(filename).suffix.lower()
    type_map = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".md": "md",
        ".txt": "txt",
    }
    file_type = type_map.get(ext)
    if not file_type:
        raise ValueError(f"不支持的文件格式: {ext}")
    return file_type
