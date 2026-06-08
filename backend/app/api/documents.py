"""文档管理路由 — /api/documents"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDetailResponse
from app.middleware.auth_middleware import get_current_user, get_current_admin
from app.services.document_service import (
    save_upload_file,
    process_document,
    reprocess_document,
    detect_file_type,
)
from app.rag.loader import load_document

router = APIRouter(prefix="/api/documents", tags=["文档管理"])


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档列表（支持分类筛选）"""
    query = select(Document)
    count_query = select(func.count(Document.id))

    if category_id:
        query = query.where(Document.category_id == category_id)
        count_query = count_query.where(Document.category_id == category_id)

    # 总数
    result = await db.execute(count_query)
    total = result.scalar()

    # 分页
    result = await db.execute(
        query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    documents = result.scalars().all()

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    category_id: int | None = Form(None),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """上传文档并开始处理"""
    # 验证文件类型
    file_type = detect_file_type(file.filename)

    # 保存文件
    file_path, stored_name = await save_upload_file(file)

    # 创建文档记录
    document = Document(
        title=file.filename,
        category_id=category_id,
        file_type=file_type,
        file_path=file_path,
        file_size=Path(file_path).stat().st_size,
        status="processing",
        uploaded_by=admin.id,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    # 同步处理文档（MVP阶段，后续改为Celery异步）
    # 注意：这里会阻塞请求直到处理完成，大文件建议用Celery
    try:
        await process_document(document.id, file_path, file_type, db)
        await db.commit()
        # 重新获取更新后的文档
        result = await db.execute(select(Document).where(Document.id == document.id))
        document = result.scalar_one()
    except Exception as e:
        await db.commit()  # 错误状态已写入
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档处理失败: {str(e)}",
        )

    return document


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文档详情（含分块列表）"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    return DocumentDetailResponse(
        id=document.id,
        title=document.title,
        category_id=document.category_id,
        file_type=document.file_type,
        file_size=document.file_size,
        chunk_count=document.chunk_count,
        status=document.status,
        error_message=document.error_message,
        uploaded_by=document.uploaded_by,
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunks=[
            {"chunk_index": c.chunk_index, "content_preview": c.content[:300]}
            for c in document.chunks
        ] if document.chunks else [],
    )


@router.get("/{document_id}/preview")
async def preview_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """预览文档原始内容"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    try:
        text = load_document(document.file_path, document.file_type)
        return {
            "title": document.title,
            "file_type": document.file_type,
            "content": text,
            "char_count": len(text),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档预览失败: {str(e)}",
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除文档（含向量和文件）"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    # 删除 Chroma 向量
    from app.rag.retriever import delete_document_from_chroma
    delete_document_from_chroma(document_id)

    # 删除物理文件
    try:
        Path(document.file_path).unlink(missing_ok=True)
    except Exception:
        pass

    # 删除数据库记录（级联删除chunks）
    await db.delete(document)
    await db.flush()


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess(
    document_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """重新处理文档"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    await reprocess_document(document_id, db)
    await db.commit()

    # 重新获取更新后的文档
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one()
