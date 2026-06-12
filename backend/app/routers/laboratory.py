from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.laboratory import Sample, DetectionTask, DetectionData, DetectionReport, QualityControl, Standard
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/laboratory", tags=["化验管理"])


# Schemas
class SampleResponse(BaseModel):
    id: int
    sample_no: str
    sample_name: str
    sample_type: Optional[str]
    sampling_point: Optional[str]
    sampling_time: datetime
    sampler_name: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SampleCreate(BaseModel):
    sample_name: str
    sample_type: Optional[str] = None
    sampling_point: Optional[str] = None
    sampling_time: datetime
    sample_volume: Optional[float] = None
    storage_condition: Optional[str] = None
    storage_location: Optional[str] = None


class DetectionTaskResponse(BaseModel):
    id: int
    task_no: str
    sample_id: Optional[int]
    detection_items: Optional[str]
    priority: str
    assigned_name: Optional[str]
    due_date: Optional[datetime]
    status: str
    progress: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DetectionDataResponse(BaseModel):
    id: int
    task_id: Optional[int]
    sample_id: Optional[int]
    parameter_name: str
    detection_method: Optional[str]
    detection_value: Optional[float]
    unit: Optional[str]
    standard_min: Optional[float]
    standard_max: Optional[float]
    is_qualified: bool
    detector_name: Optional[str]
    detection_time: Optional[datetime]
    review_status: str
    
    class Config:
        from_attributes = True


class DetectionReportResponse(BaseModel):
    id: int
    report_no: str
    task_id: Optional[int]
    report_title: Optional[str]
    conclusion: Optional[str]
    prepared_name: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QualityControlResponse(BaseModel):
    id: int
    qc_type: str
    qc_no: str
    parameter_name: Optional[str]
    standard_value: Optional[float]
    measured_value: Optional[float]
    deviation: Optional[float]
    is_qualified: Optional[bool]
    instrument_name: Optional[str]
    executor_name: Optional[str]
    execute_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class StandardResponse(BaseModel):
    id: int
    standard_type: str
    standard_no: str
    standard_name: str
    parameter_name: Optional[str]
    limit_min: Optional[float]
    limit_max: Optional[float]
    unit: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


# 样品管理
@router.get("/samples", response_model=PaginatedResponse[SampleResponse])
def get_samples(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sample_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Sample)
    if sample_type:
        query = query.filter(Sample.sample_type == sample_type)
    if status:
        query = query.filter(Sample.status == status)
    
    total = query.count()
    items = query.order_by(Sample.sampling_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/samples", response_model=SampleResponse)
def create_sample(
    data: SampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sample_no = f"SP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    sample = Sample(
        sample_no=sample_no,
        sample_name=data.sample_name,
        sample_type=data.sample_type,
        sampling_point=data.sampling_point,
        sampling_time=data.sampling_time,
        sampler_id=current_user.id,
        sampler_name=current_user.real_name or current_user.username,
        sample_volume=data.sample_volume,
        storage_condition=data.storage_condition,
        storage_location=data.storage_location
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


# 检测任务
@router.get("/tasks", response_model=PaginatedResponse[DetectionTaskResponse])
def get_detection_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DetectionTask)
    if status:
        query = query.filter(DetectionTask.status == status)
    if priority:
        query = query.filter(DetectionTask.priority == priority)
    
    total = query.count()
    items = query.order_by(DetectionTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 检测数据
@router.get("/data", response_model=PaginatedResponse[DetectionDataResponse])
def get_detection_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    task_id: Optional[int] = None,
    sample_id: Optional[int] = None,
    is_qualified: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DetectionData)
    if task_id:
        query = query.filter(DetectionData.task_id == task_id)
    if sample_id:
        query = query.filter(DetectionData.sample_id == sample_id)
    if is_qualified is not None:
        query = query.filter(DetectionData.is_qualified == is_qualified)
    
    total = query.count()
    items = query.order_by(DetectionData.detection_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 检测报告
@router.get("/reports", response_model=PaginatedResponse[DetectionReportResponse])
def get_detection_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DetectionReport)
    if status:
        query = query.filter(DetectionReport.status == status)
    
    total = query.count()
    items = query.order_by(DetectionReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 质控管理
@router.get("/qc", response_model=PaginatedResponse[QualityControlResponse])
def get_quality_controls(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    qc_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(QualityControl)
    if qc_type:
        query = query.filter(QualityControl.qc_type == qc_type)
    
    total = query.count()
    items = query.order_by(QualityControl.execute_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 标准库
@router.get("/standards", response_model=PaginatedResponse[StandardResponse])
def get_standards(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    standard_type: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Standard)
    if standard_type:
        query = query.filter(Standard.standard_type == standard_type)
    if keyword:
        query = query.filter(
            (Standard.standard_name.contains(keyword)) |
            (Standard.standard_no.contains(keyword))
        )
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
