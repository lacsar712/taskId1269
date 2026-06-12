from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.report import ReportTemplate, CustomReport
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/reports", tags=["生产报表"])


# Schemas
class ReportTemplateResponse(BaseModel):
    id: int
    name: str
    code: str
    report_type: Optional[str]
    category: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CustomReportResponse(BaseModel):
    id: int
    report_no: str
    report_name: str
    template_id: Optional[int]
    report_date: date
    start_date: Optional[date]
    end_date: Optional[date]
    summary: Optional[str]
    status: str
    created_name: Optional[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CustomReportCreate(BaseModel):
    report_name: str
    template_id: Optional[int] = None
    report_date: date
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    content: Optional[str] = None
    summary: Optional[str] = None


# 报表模板
@router.get("/templates", response_model=List[ReportTemplateResponse])
def get_report_templates(
    report_type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ReportTemplate)
    if report_type:
        query = query.filter(ReportTemplate.report_type == report_type)
    if category:
        query = query.filter(ReportTemplate.category == category)
    return query.all()


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
def get_report_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


# 自定义报表
@router.get("/custom", response_model=PaginatedResponse[CustomReportResponse])
def get_custom_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(CustomReport)
    if status:
        query = query.filter(CustomReport.status == status)
    
    total = query.count()
    items = query.order_by(CustomReport.report_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/custom", response_model=CustomReportResponse)
def create_custom_report(
    data: CustomReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    report_no = f"CR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    report = CustomReport(
        report_no=report_no,
        report_name=data.report_name,
        template_id=data.template_id,
        report_date=data.report_date,
        start_date=data.start_date,
        end_date=data.end_date,
        content=data.content,
        summary=data.summary,
        created_by=current_user.id,
        created_name=current_user.real_name or current_user.username
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/custom/{report_id}", response_model=CustomReportResponse)
def get_custom_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    report = db.query(CustomReport).filter(CustomReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    return report


# 数据统计接口
@router.get("/statistics/daily")
def get_daily_statistics(
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取日报统计数据"""
    return {
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "water_intake": 15000,
        "water_output": 14500,
        "power_consumption": 12500,
        "chemical_usage": 350,
        "cod_inlet": 180,
        "cod_outlet": 25,
        "nh3n_inlet": 35,
        "nh3n_outlet": 3,
        "sludge_output": 25
    }


@router.get("/statistics/monthly")
def get_monthly_statistics(
    year: int = Query(default=2024),
    month: int = Query(default=1, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取月报统计数据"""
    return {
        "year": year,
        "month": month,
        "total_water_intake": 450000,
        "total_water_output": 435000,
        "total_power_consumption": 375000,
        "avg_cod_removal_rate": 88.5,
        "avg_nh3n_removal_rate": 91.4,
        "total_chemical_cost": 125000,
        "total_power_cost": 285000
    }
