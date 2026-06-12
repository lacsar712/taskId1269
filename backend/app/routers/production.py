from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.production import ProcessParameter, ProductionPlan, ProductionLog, AbnormalAlarm, ProcessOptimization
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/production", tags=["生产管理"])


# Schemas
class ProcessParameterResponse(BaseModel):
    id: int
    name: str
    code: str
    unit: Optional[str]
    current_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    standard_value: Optional[float]
    process_section: Optional[str]
    status: Optional[str]
    recorded_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProductionPlanResponse(BaseModel):
    id: int
    plan_no: str
    plan_date: datetime
    target_volume: Optional[float]
    actual_volume: Optional[float]
    operation_mode: Optional[str]
    description: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProductionPlanCreate(BaseModel):
    plan_date: datetime
    target_volume: Optional[float] = None
    operation_mode: Optional[str] = None
    description: Optional[str] = None


class ProductionLogResponse(BaseModel):
    id: int
    log_date: datetime
    shift: Optional[str]
    log_type: Optional[str]
    content: str
    operator_name: Optional[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProductionLogCreate(BaseModel):
    log_date: datetime
    shift: Optional[str] = None
    log_type: str = "manual"
    content: str


class AbnormalAlarmResponse(BaseModel):
    id: int
    alarm_no: str
    alarm_type: str
    alarm_level: str
    title: str
    description: Optional[str]
    source: Optional[str]
    current_value: Optional[float]
    threshold_value: Optional[float]
    status: str
    handler_name: Optional[str]
    handle_time: Optional[datetime]
    alarm_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class HandleAlarmRequest(BaseModel):
    handle_result: str


class ProcessOptimizationResponse(BaseModel):
    id: int
    title: str
    optimization_type: Optional[str]
    current_situation: Optional[str]
    suggestion: str
    expected_effect: Optional[str]
    priority: int
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# 工艺参数监控
@router.get("/parameters", response_model=List[ProcessParameterResponse])
def get_process_parameters(
    process_section: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ProcessParameter)
    if process_section:
        query = query.filter(ProcessParameter.process_section == process_section)
    return query.order_by(ProcessParameter.process_section).all()


@router.get("/parameters/{param_id}", response_model=ProcessParameterResponse)
def get_process_parameter(
    param_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    param = db.query(ProcessParameter).filter(ProcessParameter.id == param_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="参数不存在")
    return param


# 生产计划
@router.get("/plans", response_model=PaginatedResponse[ProductionPlanResponse])
def get_production_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ProductionPlan)
    if status:
        query = query.filter(ProductionPlan.status == status)
    
    total = query.count()
    items = query.order_by(ProductionPlan.plan_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/plans", response_model=ProductionPlanResponse)
def create_production_plan(
    plan_data: ProductionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    plan_no = f"PP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    plan = ProductionPlan(
        plan_no=plan_no,
        plan_date=plan_data.plan_date,
        target_volume=plan_data.target_volume,
        operation_mode=plan_data.operation_mode,
        description=plan_data.description,
        created_by=current_user.id
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


# 生产日志
@router.get("/logs", response_model=PaginatedResponse[ProductionLogResponse])
def get_production_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    log_type: Optional[str] = None,
    shift: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ProductionLog)
    if log_type:
        query = query.filter(ProductionLog.log_type == log_type)
    if shift:
        query = query.filter(ProductionLog.shift == shift)
    
    total = query.count()
    items = query.order_by(ProductionLog.log_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/logs", response_model=ProductionLogResponse)
def create_production_log(
    log_data: ProductionLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    log = ProductionLog(
        log_date=log_data.log_date,
        shift=log_data.shift,
        log_type=log_data.log_type,
        content=log_data.content,
        operator_id=current_user.id,
        operator_name=current_user.real_name or current_user.username
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# 异常告警
@router.get("/alarms", response_model=PaginatedResponse[AbnormalAlarmResponse])
def get_abnormal_alarms(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    alarm_level: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(AbnormalAlarm)
    if alarm_level:
        query = query.filter(AbnormalAlarm.alarm_level == alarm_level)
    if status:
        query = query.filter(AbnormalAlarm.status == status)
    
    total = query.count()
    items = query.order_by(AbnormalAlarm.alarm_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=[AbnormalAlarmResponse(
            id=a.id,
            alarm_no=a.alarm_no,
            alarm_type=a.alarm_type,
            alarm_level=a.alarm_level if a.alarm_level else 'normal',
            title=a.title,
            description=a.description,
            source=a.source,
            current_value=a.current_value,
            threshold_value=a.threshold_value,
            status=a.status if a.status else 'pending',
            handler_name=a.handler_name,
            handle_time=a.handle_time,
            alarm_time=a.alarm_time
        ) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.put("/alarms/{alarm_id}/handle", response_model=MessageResponse)
def handle_alarm(
    alarm_id: int,
    data: HandleAlarmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    alarm = db.query(AbnormalAlarm).filter(AbnormalAlarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="告警不存在")
    
    alarm.status = "resolved"
    alarm.handler_id = current_user.id
    alarm.handler_name = current_user.real_name or current_user.username
    alarm.handle_time = datetime.now()
    alarm.handle_result = data.handle_result
    db.commit()
    
    return MessageResponse(message="处理成功")


# 工艺优化
@router.get("/optimizations", response_model=List[ProcessOptimizationResponse])
def get_process_optimizations(
    optimization_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ProcessOptimization)
    if optimization_type:
        query = query.filter(ProcessOptimization.optimization_type == optimization_type)
    if status:
        query = query.filter(ProcessOptimization.status == status)
    return query.order_by(ProcessOptimization.priority.desc()).all()
