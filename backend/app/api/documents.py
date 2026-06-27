"""文档管理路由 — /api/documents"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document, DocDepartment
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


def _build_access_filter(user: User):
    """构建文档访问权限过滤条件

    Admin: 全部可见
    普通用户: public 文档 + 本部门 department 文档 + restricted 中共享给本部门的
    """
    if user.role == "admin":
        return None  # 无过滤

    conditions = [Document.visibility == "public"]
    if user.department_id:
        conditions.append(
            (Document.visibility == "department") & (Document.department_id == user.department_id)
        )
        # restricted 中共享给本部门的
        shared_subq = (
            select(DocDepartment.document_id)
            .where(DocDepartment.department_id == user.department_id)
        )
        conditions.append(Document.id.in_(shared_subq))

    return or_(*conditions)


async def _check_document_access(document_id: int, user: User, db: AsyncSession) -> Document:
    """检查用户是否有权访问指定文档，返回文档或抛出404"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    if user.role == "admin":
        return doc

    # 普通用户：检查权限
    if doc.visibility == "public":
        return doc
    if doc.visibility == "department" and user.department_id == doc.department_id:
        return doc
    if doc.visibility == "restricted" and user.department_id:
        shared = await db.execute(
            select(DocDepartment).where(
                DocDepartment.document_id == doc.id,
                DocDepartment.department_id == user.department_id,
            )
        )
        if shared.scalar_one_or_none():
            return doc

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档列表（支持分类筛选 + 部门权限过滤）"""
    query = select(Document)
    count_query = select(func.count(Document.id))

    # 权限过滤
    access_filter = _build_access_filter(user)
    if access_filter is not None:
        query = query.where(access_filter)
        count_query = count_query.where(access_filter)

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
    visibility: str = Form("public"),
    department_id: int | None = Form(None),
    shared_department_ids: str | None = Form(None, description="逗号分隔的共享部门ID列表，仅visibility=restricted时有效"),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """上传文档并开始处理（仅管理员）"""
    # 验证文件类型
    file_type = detect_file_type(file.filename)

    # 验证 visibility
    if visibility not in ("public", "department", "restricted"):
        raise HTTPException(status_code=400, detail="visibility 必须为 public/department/restricted")
    if visibility == "department" and not department_id:
        raise HTTPException(status_code=400, detail="department 可见性需要指定 department_id")

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
        department_id=department_id,
        visibility=visibility,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    # 处理 restricted 共享部门
    if visibility == "restricted" and shared_department_ids:
        for dept_id_str in shared_department_ids.split(","):
            try:
                dept_id = int(dept_id_str.strip())
                db.add(DocDepartment(document_id=document.id, department_id=dept_id))
            except ValueError:
                pass
    elif visibility == "department" and department_id:
        # department 可见性自动添加与所属部门的关联
        db.add(DocDepartment(document_id=document.id, department_id=department_id))

    await db.flush()

    # 同步处理文档
    try:
        await process_document(document.id, file_path, file_type, db)
        await db.commit()
        result = await db.execute(select(Document).where(Document.id == document.id))
        document = result.scalar_one()
    except Exception as e:
        await db.commit()
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
    """获取文档详情（含分块列表 + 权限检查）"""
    document = await _check_document_access(document_id, user, db)

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
        department_id=document.department_id,
        visibility=document.visibility,
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
    """预览文档原始内容（权限检查）"""
    document = await _check_document_access(document_id, user, db)

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
    """删除文档（仅管理员，含向量和文件）"""
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

    # 删除关联（document_departments 由 CASCADE 自动删除）
    await db.delete(document)
    await db.flush()


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess(
    document_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """重新处理文档（仅管理员）"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    await reprocess_document(document_id, db)
    await db.commit()

    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one()
