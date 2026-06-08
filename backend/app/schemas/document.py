"""文档管理 Pydantic 模型"""

from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    title: str
    category_id: int | None
    file_type: str
    file_size: int | None
    chunk_count: int
    status: str
    error_message: str | None = None
    uploaded_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChunkPreview(BaseModel):
    chunk_index: int
    content_preview: str


class DocumentDetailResponse(DocumentResponse):
    chunks: list[ChunkPreview] = []


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
