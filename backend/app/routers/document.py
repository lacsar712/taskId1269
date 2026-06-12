from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentCategory
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/documents", tags=["资料管理"])


# Schemas
class DocumentCategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    parent_id: int
    sort_order: int
    description: Optional[str]
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    doc_no: str
    title: str
    category_id: Optional[int]
    file_name: Optional[str]
    file_size: Optional[int]
    file_type: Optional[str]
    version: str
    description: Optional[str]
    uploader_name: Optional[str]
    review_status: str
    download_count: int
    is_archived: bool
    is_favorite: bool
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    tags: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    description: Optional[str] = None


# 文档分类
@router.get("/categories", response_model=List[DocumentCategoryResponse])
def get_document_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(DocumentCategory).order_by(DocumentCategory.sort_order).all()


@router.post("/categories", response_model=DocumentCategoryResponse)
def create_document_category(
    name: str,
    parent_id: int = 0,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    code = f"DC{datetime.now().strftime('%Y%m%d%H%M%S')}"
    category = DocumentCategory(
        name=name,
        code=code,
        parent_id=parent_id,
        description=description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# 文档管理
@router.get("", response_model=PaginatedResponse[DocumentResponse])
def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    file_type: Optional[str] = None,
    is_archived: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Document)
    if category_id:
        query = query.filter(Document.category_id == category_id)
    if keyword:
        query = query.filter(
            (Document.title.contains(keyword)) |
            (Document.doc_no.contains(keyword))
        )
    if file_type:
        query = query.filter(Document.file_type == file_type)
    if is_archived is not None:
        query = query.filter(Document.is_archived == is_archived)
    
    total = query.count()
    items = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=DocumentResponse)
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    doc_no = f"DOC{datetime.now().strftime('%Y%m%d%H%M%S')}"
    document = Document(
        doc_no=doc_no,
        title=data.title,
        category_id=data.category_id,
        tags=data.tags,
        file_name=data.file_name,
        file_path=data.file_path,
        file_size=data.file_size,
        file_type=data.file_type,
        description=data.description,
        uploader_id=current_user.id,
        uploader_name=current_user.real_name or current_user.username
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@router.put("/{doc_id}/favorite", response_model=MessageResponse)
def toggle_favorite(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    document.is_favorite = not document.is_favorite
    db.commit()
    
    return MessageResponse(message="操作成功")


@router.put("/{doc_id}/archive", response_model=MessageResponse)
def archive_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    document.is_archived = True
    document.archive_date = datetime.now()
    db.commit()
    
    return MessageResponse(message="归档成功")


@router.delete("/{doc_id}", response_model=MessageResponse)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    db.delete(document)
    db.commit()
    
    return MessageResponse(message="删除成功")


# 热门文档
@router.get("/hot/list", response_model=List[DocumentResponse])
def get_hot_documents(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Document).filter(
        Document.is_archived == False
    ).order_by(Document.download_count.desc()).limit(limit).all()


# 收藏文档
@router.get("/favorites/list", response_model=List[DocumentResponse])
def get_favorite_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Document).filter(Document.is_favorite == True).all()
