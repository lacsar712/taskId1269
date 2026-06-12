from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.energy import EnergyData, EnergySavingPlan, EnergyCost
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/energy", tags=["能耗管理"])


# Schemas
class EnergyDataResponse(BaseModel):
    id: int
    data_type: str
    equipment_id: Optional[int]
    process_section: Optional[str]
    meter_id: Optional[str]
    reading_value: Optional[float]
    consumption: Optional[float]
    unit: Optional[str]
    total_cost: Optional[float]
    record_time: datetime
    status: str
    
    class Config:
        from_attributes = True


class EnergySavingPlanResponse(BaseModel):
    id: int
    plan_no: str
    plan_name: str
    plan_type: Optional[str]
    target_section: Optional[str]
    current_consumption: Optional[float]
    target_consumption: Optional[float]
    saving_rate: Optional[float]
    start_date: Optional[date]
    end_date: Optional[date]
    actual_saving: Optional[float]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EnergyCostResponse(BaseModel):
    id: int
    cost_date: date
    cost_type: Optional[str]
    department: Optional[str]
    consumption: Optional[float]
    unit_price: Optional[float]
    total_cost: Optional[float]
    budget: Optional[float]
    variance: Optional[float]
    
    class Config:
        from_attributes = True


# 能耗实时监测
@router.get("/realtime", response_model=List[EnergyDataResponse])
def get_realtime_energy_data(
    data_type: Optional[str] = None,
    process_section: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(EnergyData)
    if data_type:
        query = query.filter(EnergyData.data_type == data_type)
    if process_section:
        query = query.filter(EnergyData.process_section == process_section)
    return query.order_by(EnergyData.record_time.desc()).limit(100).all()


@router.get("/history", response_model=PaginatedResponse[EnergyDataResponse])
def get_energy_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    data_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(EnergyData)
    if data_type:
        query = query.filter(EnergyData.data_type == data_type)
    
    total = query.count()
    items = query.order_by(EnergyData.record_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 能耗分析
@router.get("/analysis/section")
def get_section_energy_analysis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """工艺段能耗分析"""
    return [
        {"section": "预处理", "electricity": 2500, "water": 100, "gas": 50, "total_cost": 2150},
        {"section": "生化处理", "electricity": 8500, "water": 200, "gas": 80, "total_cost": 7230},
        {"section": "深度处理", "electricity": 3200, "water": 150, "gas": 30, "total_cost": 2720},
        {"section": "污泥处理", "electricity": 1800, "water": 80, "gas": 20, "total_cost": 1530},
        {"section": "辅助系统", "electricity": 1500, "water": 50, "gas": 10, "total_cost": 1275}
    ]


@router.get("/analysis/equipment")
def get_equipment_energy_analysis(
    process_section: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """设备能耗分析"""
    return [
        {"equipment": "曝气风机#1", "consumption": 3500, "running_hours": 720, "efficiency": 0.85},
        {"equipment": "曝气风机#2", "consumption": 3200, "running_hours": 680, "efficiency": 0.82},
        {"equipment": "提升泵#1", "consumption": 1200, "running_hours": 700, "efficiency": 0.78},
        {"equipment": "提升泵#2", "consumption": 1100, "running_hours": 650, "efficiency": 0.75},
        {"equipment": "污泥泵", "consumption": 800, "running_hours": 400, "efficiency": 0.80}
    ]


# 节能策略
@router.get("/saving/plans", response_model=PaginatedResponse[EnergySavingPlanResponse])
def get_energy_saving_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(EnergySavingPlan)
    if status:
        query = query.filter(EnergySavingPlan.status == status)
    
    total = query.count()
    items = query.order_by(EnergySavingPlan.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/saving/suggestions")
def get_energy_saving_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """智能节能建议"""
    return [
        {
            "id": 1,
            "title": "优化曝气量调节",
            "description": "根据实时DO值自动调节曝气量，预计节能15%",
            "expected_saving": 1500,
            "priority": "high"
        },
        {
            "id": 2,
            "title": "调整泵组运行策略",
            "description": "采用变频调速，优化泵组运行组合",
            "expected_saving": 800,
            "priority": "medium"
        },
        {
            "id": 3,
            "title": "错峰用电优化",
            "description": "将非紧急操作调整至低谷电价时段",
            "expected_saving": 500,
            "priority": "low"
        }
    ]


# 能耗成本
@router.get("/costs", response_model=PaginatedResponse[EnergyCostResponse])
def get_energy_costs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    cost_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(EnergyCost)
    if cost_type:
        query = query.filter(EnergyCost.cost_type == cost_type)
    
    total = query.count()
    items = query.order_by(EnergyCost.cost_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/costs/summary")
def get_energy_cost_summary(
    year: int = Query(default=2024),
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """能耗成本汇总"""
    return {
        "year": year,
        "month": month,
        "electricity_cost": 285000,
        "water_cost": 15000,
        "gas_cost": 8000,
        "total_cost": 308000,
        "budget": 320000,
        "variance": -12000,
        "yoy_change": -5.2,
        "mom_change": -2.1
    }
