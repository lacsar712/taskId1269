from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class DocumentCategory(Base):
    """文档分类"""
    __tablename__ = "document_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    parent_id = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    permissions = Column(Text)  # 权限配置JSON
    description = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class Document(Base):
    """文档管理"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_no = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    category_id = Column(Integer)
    tags = Column(Text)  # 标签JSON
    file_name = Column(String(200))
    file_path = Column(String(500))
    file_size = Column(Integer)  # 文件大小(bytes)
    file_type = Column(String(50))  # pdf, doc, xls等
    version = Column(String(20), default="1.0")
    description = Column(Text)
    uploader_id = Column(Integer)
    uploader_name = Column(String(50))
    reviewer_id = Column(Integer)
    review_status = Column(String(20), default="pending")  # pending, approved, rejected
    download_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    archive_date = Column(DateTime)
    expiry_date = Column(DateTime)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
