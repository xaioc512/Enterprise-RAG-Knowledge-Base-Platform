"""文档与分块模型"""

from datetime import datetime
from sqlalchemy import String, Text, Integer, Enum, DateTime, ForeignKey, func, Table, Column, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# 文档-部门多对多关联表（restricted 可见性）
class DocDepartment(Base):
    __tablename__ = "document_departments"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    file_type: Mapped[str] = mapped_column(
        Enum("pdf", "docx", "md", "txt", name="file_type"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        Enum("processing", "done", "error", name="doc_status"),
        default="processing",
    )
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True, index=True
    )
    visibility: Mapped[str] = mapped_column(
        Enum("public", "department", "restricted", name="doc_visibility"),
        nullable=False,
        default="public",
    )
    # 智能标注字段
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suggested_category_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    shared_departments: Mapped[list[int]] = relationship(
        "Department",
        secondary="document_departments",
        primaryjoin="Document.id == DocDepartment.document_id",
        secondaryjoin="DocDepartment.department_id == Department.id",
        viewonly=True,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
