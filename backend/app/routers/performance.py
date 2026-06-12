from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.performance import PerformanceIndicator, PerformanceData, PerformanceResult
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/performance", tags=["绩效管理"])


# Schemas
class PerformanceIndicatorResponse(BaseModel):
    id: int
    name: str
    code: str
    category: Optional[str]
    indicator_type: Optional[str]
    unit: Optional[str]
    weight: float
    target_value: Optional[float]
    min_score: float
    max_score: float
    data_source: Optional[str]
    is_auto_collect: bool
    status: str
    
    class Config:
        from_attributes = True


class PerformanceIndicatorCreate(BaseModel):
    name: str
    category: Optional[str] = None
    indicator_type: Optional[str] = None
    unit: Optional[str] = None
    weight: float = 1.0
    target_value: Optional[float] = None
    scoring_rules: Optional[str] = None
    data_source: Optional[str] = None
    is_auto_collect: bool = False


class PerformanceDataResponse(BaseModel):
    id: int
    indicator_id: int
    user_id: Optional[int]
    team_id: Optional[int]
    period_type: Optional[str]
    period_date: date
    actual_value: Optional[float]
    score: Optional[float]
    data_source: Optional[str]
    review_status: str
    
    class Config:
        from_attributes = True


class PerformanceResultResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_name: Optional[str]
    team_id: Optional[int]
    team_name: Optional[str]
    period_type: Optional[str]
    period_start: Optional[date]
    period_end: Optional[date]
    total_score: Optional[float]
    rank: Optional[int]
    level: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


# 考核指标
@router.get("/indicators", response_model=PaginatedResponse[PerformanceIndicatorResponse])
def get_performance_indicators(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PerformanceIndicator)
    if category:
        query = query.filter(PerformanceIndicator.category == category)
    if status:
        query = query.filter(PerformanceIndicator.status == status)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/indicators", response_model=PerformanceIndicatorResponse)
def create_performance_indicator(
    data: PerformanceIndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    code = f"PI{datetime.now().strftime('%Y%m%d%H%M%S')}"
    indicator = PerformanceIndicator(
        name=data.name,
        code=code,
        category=data.category,
        indicator_type=data.indicator_type,
        unit=data.unit,
        weight=data.weight,
        target_value=data.target_value,
        scoring_rules=data.scoring_rules,
        data_source=data.data_source,
        is_auto_collect=data.is_auto_collect
    )
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


# 绩效数据
@router.get("/data", response_model=PaginatedResponse[PerformanceDataResponse])
def get_performance_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    indicator_id: Optional[int] = None,
    user_id: Optional[int] = None,
    period_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PerformanceData)
    if indicator_id:
        query = query.filter(PerformanceData.indicator_id == indicator_id)
    if user_id:
        query = query.filter(PerformanceData.user_id == user_id)
    if period_type:
        query = query.filter(PerformanceData.period_type == period_type)
    
    total = query.count()
    items = query.order_by(PerformanceData.period_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 绩效结果
@router.get("/results", response_model=PaginatedResponse[PerformanceResultResponse])
def get_performance_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    period_type: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PerformanceResult)
    if period_type:
        query = query.filter(PerformanceResult.period_type == period_type)
    if level:
        query = query.filter(PerformanceResult.level == level)
    
    total = query.count()
    items = query.order_by(PerformanceResult.total_score.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 统计分析
@router.get("/statistics/personal")
def get_personal_statistics(
    user_id: Optional[int] = None,
    period_type: str = Query(default="monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """个人绩效统计"""
    target_user_id = user_id or current_user.id
    return {
        "user_id": target_user_id,
        "period_type": period_type,
        "current_score": 85.5,
        "rank": 3,
        "total_members": 25,
        "level": "A",
        "trend": [82, 84, 85, 83, 86, 85.5],
        "indicators": [
            {"name": "工作完成率", "score": 90, "weight": 0.3},
            {"name": "质量达标率", "score": 88, "weight": 0.25},
            {"name": "安全执行", "score": 85, "weight": 0.2},
            {"name": "团队协作", "score": 80, "weight": 0.15},
            {"name": "创新改进", "score": 78, "weight": 0.1}
        ]
    }


@router.get("/statistics/team")
def get_team_statistics(
    team_id: Optional[int] = None,
    period_type: str = Query(default="monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """班组绩效统计"""
    return {
        "team_id": team_id,
        "period_type": period_type,
        "teams": [
            {"name": "甲班", "score": 88.5, "rank": 1, "members": 8},
            {"name": "乙班", "score": 86.2, "rank": 2, "members": 8},
            {"name": "丙班", "score": 84.8, "rank": 3, "members": 7},
            {"name": "丁班", "score": 82.3, "rank": 4, "members": 8}
        ],
        "comparison": {
            "production": [88, 85, 83, 80],
            "safety": [90, 88, 87, 85],
            "quality": [87, 86, 84, 82]
        }
    }
