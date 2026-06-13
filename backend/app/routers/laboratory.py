from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.laboratory import Sample, DetectionTask, DetectionData, DetectionReport, QualityControl, Standard, Reagent, ReagentReplenishment
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


# 试剂库存管理 - Schemas
class ReagentResponse(BaseModel):
    id: int
    reagent_no: str
    name: str
    specification: Optional[str]
    manufacturer: Optional[str]
    current_stock: float
    min_safe_stock: float
    storage_location: Optional[str]
    expiry_date: Optional[str]
    unit: str
    category: Optional[str]
    purity: Optional[str]
    cas_no: Optional[str]
    remarks: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReagentCreate(BaseModel):
    name: str
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    current_stock: float = 0
    min_safe_stock: float = 0
    storage_location: Optional[str] = None
    expiry_date: Optional[str] = None
    unit: str = "瓶"
    category: Optional[str] = None
    purity: Optional[str] = None
    cas_no: Optional[str] = None
    remarks: Optional[str] = None


class ReagentUpdate(BaseModel):
    name: Optional[str] = None
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    current_stock: Optional[float] = None
    min_safe_stock: Optional[float] = None
    storage_location: Optional[str] = None
    expiry_date: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    purity: Optional[str] = None
    cas_no: Optional[str] = None
    remarks: Optional[str] = None
    status: Optional[str] = None


class ReagentStatsResponse(BaseModel):
    total: int
    low_stock: int
    near_expiry: int
    categories: int


# 试剂库存管理 - APIs
@router.get("/reagents", response_model=PaginatedResponse[ReagentResponse])
def get_reagents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    low_stock_only: Optional[bool] = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Reagent)
    if keyword:
        query = query.filter(
            (Reagent.name.contains(keyword)) |
            (Reagent.reagent_no.contains(keyword)) |
            (Reagent.manufacturer.contains(keyword))
        )
    if category:
        query = query.filter(Reagent.category == category)
    if status:
        query = query.filter(Reagent.status == status)
    if low_stock_only:
        query = query.filter(Reagent.current_stock <= Reagent.min_safe_stock)
    
    total = query.count()
    items = query.order_by(Reagent.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/reagents/stats", response_model=ReagentStatsResponse)
def get_reagent_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    total = db.query(Reagent).filter(Reagent.status == "active").count()
    low_stock = db.query(Reagent).filter(
        Reagent.status == "active",
        Reagent.current_stock <= Reagent.min_safe_stock
    ).count()
    
    from sqlalchemy import func
    from datetime import date, timedelta
    thirty_days_later = date.today() + timedelta(days=30)
    near_expiry = db.query(Reagent).filter(
        Reagent.status == "active",
        Reagent.expiry_date != None,
        Reagent.expiry_date <= thirty_days_later
    ).count()
    
    categories = db.query(func.count(func.distinct(Reagent.category))).scalar() or 0
    
    return ReagentStatsResponse(
        total=total,
        low_stock=low_stock,
        near_expiry=near_expiry,
        categories=categories
    )


@router.get("/reagents/{reagent_id}", response_model=ReagentResponse)
def get_reagent(
    reagent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    reagent = db.query(Reagent).filter(Reagent.id == reagent_id).first()
    if not reagent:
        raise HTTPException(status_code=404, detail="试剂不存在")
    return reagent


@router.post("/reagents", response_model=ReagentResponse)
def create_reagent(
    data: ReagentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    reagent_no = f"RGT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    expiry_date_val = None
    if data.expiry_date:
        from datetime import datetime as dt
        expiry_date_val = dt.strptime(data.expiry_date, "%Y-%m-%d").date()
    
    reagent = Reagent(
        reagent_no=reagent_no,
        name=data.name,
        specification=data.specification,
        manufacturer=data.manufacturer,
        current_stock=data.current_stock,
        min_safe_stock=data.min_safe_stock,
        storage_location=data.storage_location,
        expiry_date=expiry_date_val,
        unit=data.unit,
        category=data.category,
        purity=data.purity,
        cas_no=data.cas_no,
        remarks=data.remarks
    )
    db.add(reagent)
    db.commit()
    db.refresh(reagent)
    return reagent


@router.put("/reagents/{reagent_id}", response_model=ReagentResponse)
def update_reagent(
    reagent_id: int,
    data: ReagentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    reagent = db.query(Reagent).filter(Reagent.id == reagent_id).first()
    if not reagent:
        raise HTTPException(status_code=404, detail="试剂不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    
    if "expiry_date" in update_data and update_data["expiry_date"]:
        from datetime import datetime as dt
        update_data["expiry_date"] = dt.strptime(update_data["expiry_date"], "%Y-%m-%d").date()
    elif "expiry_date" in update_data:
        update_data["expiry_date"] = None
    
    for key, value in update_data.items():
        setattr(reagent, key, value)
    
    db.commit()
    db.refresh(reagent)
    return reagent


@router.delete("/reagents/{reagent_id}", response_model=MessageResponse)
def delete_reagent(
    reagent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    reagent = db.query(Reagent).filter(Reagent.id == reagent_id).first()
    if not reagent:
        raise HTTPException(status_code=404, detail="试剂不存在")
    
    reagent.status = "inactive"
    db.commit()
    return MessageResponse(message="删除成功")


@router.get("/reagents/categories/list")
def get_reagent_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from sqlalchemy import func
    categories = db.query(
        Reagent.category,
        func.count(Reagent.id).label("count")
    ).filter(
        Reagent.category != None,
        Reagent.status == "active"
    ).group_by(Reagent.category).all()
    
    return [{"name": cat[0], "count": cat[1]} for cat in categories]


# 补货申请管理 - Schemas
class ReagentReplenishmentResponse(BaseModel):
    id: int
    application_no: str
    reagent_id: int
    reagent_name: Optional[str]
    specification: Optional[str]
    apply_quantity: float
    unit: Optional[str]
    urgency: str
    purpose: Optional[str]
    applicant_name: Optional[str]
    apply_time: Optional[datetime]
    status: str
    approver_name: Optional[str]
    approve_time: Optional[datetime]
    approve_remark: Optional[str]
    purchase_quantity: Optional[float]
    purchase_status: str
    purchaser: Optional[str]
    expected_date: Optional[str]
    purchase_remark: Optional[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReplenishmentCreate(BaseModel):
    reagent_id: int
    apply_quantity: float
    urgency: str = "normal"
    purpose: Optional[str] = None


class ReplenishmentApprove(BaseModel):
    status: str
    approve_remark: Optional[str] = None
    purchase_quantity: Optional[float] = None


class ReplenishmentPurchaseUpdate(BaseModel):
    purchase_status: str
    purchaser: Optional[str] = None
    expected_date: Optional[str] = None
    purchase_remark: Optional[str] = None


# 补货申请管理 - APIs
@router.get("/reagent-replenishments", response_model=PaginatedResponse[ReagentReplenishmentResponse])
def get_replenishments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    purchase_status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ReagentReplenishment)
    if status:
        query = query.filter(ReagentReplenishment.status == status)
    if urgency:
        query = query.filter(ReagentReplenishment.urgency == urgency)
    if purchase_status:
        query = query.filter(ReagentReplenishment.purchase_status == purchase_status)
    if keyword:
        query = query.filter(
            (ReagentReplenishment.reagent_name.contains(keyword)) |
            (ReagentReplenishment.application_no.contains(keyword))
        )
    
    total = query.count()
    items = query.order_by(ReagentReplenishment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/reagent-replenishments/{replenishment_id}", response_model=ReagentReplenishmentResponse)
def get_replenishment(
    replenishment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    replenishment = db.query(ReagentReplenishment).filter(
        ReagentReplenishment.id == replenishment_id
    ).first()
    if not replenishment:
        raise HTTPException(status_code=404, detail="补货申请不存在")
    return replenishment


@router.post("/reagent-replenishments", response_model=ReagentReplenishmentResponse)
def create_replenishment(
    data: ReplenishmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    reagent = db.query(Reagent).filter(Reagent.id == data.reagent_id).first()
    if not reagent:
        raise HTTPException(status_code=404, detail="试剂不存在")
    
    application_no = f"RPL{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    replenishment = ReagentReplenishment(
        application_no=application_no,
        reagent_id=data.reagent_id,
        reagent_name=reagent.name,
        specification=reagent.specification,
        apply_quantity=data.apply_quantity,
        unit=reagent.unit,
        urgency=data.urgency,
        purpose=data.purpose,
        applicant_id=current_user.id,
        applicant_name=current_user.real_name or current_user.username
    )
    db.add(replenishment)
    db.commit()
    db.refresh(replenishment)
    return replenishment


@router.put("/reagent-replenishments/{replenishment_id}/approve", response_model=ReagentReplenishmentResponse)
def approve_replenishment(
    replenishment_id: int,
    data: ReplenishmentApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    replenishment = db.query(ReagentReplenishment).filter(
        ReagentReplenishment.id == replenishment_id
    ).first()
    if not replenishment:
        raise HTTPException(status_code=404, detail="补货申请不存在")
    
    if replenishment.status != "pending":
        raise HTTPException(status_code=400, detail="该申请已处理")
    
    replenishment.status = data.status
    replenishment.approver_id = current_user.id
    replenishment.approver_name = current_user.real_name or current_user.username
    replenishment.approve_time = datetime.now()
    replenishment.approve_remark = data.approve_remark
    
    if data.status == "approved":
        replenishment.purchase_status = "not_started"
        if data.purchase_quantity:
            replenishment.purchase_quantity = data.purchase_quantity
        else:
            replenishment.purchase_quantity = replenishment.apply_quantity
    
    db.commit()
    db.refresh(replenishment)
    return replenishment


@router.put("/reagent-replenishments/{replenishment_id}/purchase", response_model=ReagentReplenishmentResponse)
def update_purchase_status(
    replenishment_id: int,
    data: ReplenishmentPurchaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    replenishment = db.query(ReagentReplenishment).filter(
        ReagentReplenishment.id == replenishment_id
    ).first()
    if not replenishment:
        raise HTTPException(status_code=404, detail="补货申请不存在")
    
    if replenishment.status != "approved" and replenishment.status != "purchasing":
        raise HTTPException(status_code=400, detail="该申请状态不允许更新采购进度")
    
    replenishment.purchase_status = data.purchase_status
    if data.purchaser:
        replenishment.purchaser = data.purchaser
    
    if data.expected_date:
        from datetime import datetime as dt
        replenishment.expected_date = dt.strptime(data.expected_date, "%Y-%m-%d").date()
    
    if data.purchase_remark:
        replenishment.purchase_remark = data.purchase_remark
    
    if data.purchase_status == "completed" and replenishment.purchase_quantity:
        reagent = db.query(Reagent).filter(Reagent.id == replenishment.reagent_id).first()
        if reagent:
            reagent.current_stock += replenishment.purchase_quantity
    
    if data.purchase_status == "completed":
        replenishment.status = "completed"
    elif data.purchase_status == "in_progress" or data.purchase_status == "delivered":
        replenishment.status = "purchasing"
    
    db.commit()
    db.refresh(replenishment)
    return replenishment
