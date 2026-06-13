from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.production import (
    ProcessParameter, ProductionPlan, ProductionLog, 
    AbnormalAlarm, ProcessOptimization,
    ShiftHandover, HandoverFollowUp
)
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


# ================ 值班交接班 ================

class HandoverFollowUpBase(BaseModel):
    content: str
    priority: Optional[str] = "normal"
    deadline: Optional[datetime] = None
    responsible_person: Optional[str] = None
    status: Optional[str] = "pending"
    remark: Optional[str] = None


class HandoverFollowUpCreate(HandoverFollowUpBase):
    pass


class HandoverFollowUpUpdate(HandoverFollowUpBase):
    id: Optional[int] = None


class HandoverFollowUpResponse(BaseModel):
    id: int
    content: str
    priority: Optional[str]
    deadline: Optional[datetime]
    responsible_person: Optional[str]
    status: Optional[str]
    completed_time: Optional[datetime]
    remark: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ShiftHandoverBase(BaseModel):
    shift_type: str
    shift_date: datetime
    start_time: datetime
    end_time: datetime
    handover_person_id: Optional[int] = None
    handover_person_name: Optional[str] = None
    takeover_person_id: Optional[int] = None
    takeover_person_name: Optional[str] = None
    water_volume_summary: Optional[str] = None
    water_quality_summary: Optional[str] = None
    equipment_status: Optional[str] = None
    abnormal_notes: Optional[str] = None
    remark: Optional[str] = None


class ShiftHandoverCreate(ShiftHandoverBase):
    follow_up_items: Optional[List[HandoverFollowUpCreate]] = None


class ShiftHandoverUpdate(ShiftHandoverBase):
    status: Optional[str] = None
    follow_up_items: Optional[List[HandoverFollowUpUpdate]] = None


class ShiftHandoverResponse(BaseModel):
    id: int
    handover_no: str
    shift_type: str
    shift_date: datetime
    start_time: datetime
    end_time: datetime
    handover_person_id: Optional[int]
    handover_person_name: Optional[str]
    takeover_person_id: Optional[int]
    takeover_person_name: Optional[str]
    water_volume_summary: Optional[str]
    water_quality_summary: Optional[str]
    equipment_status: Optional[str]
    abnormal_notes: Optional[str]
    status: str
    handover_confirm_time: Optional[datetime]
    takeover_confirm_time: Optional[datetime]
    handover_signature: Optional[str]
    takeover_signature: Optional[str]
    remark: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    follow_up_items: Optional[List[HandoverFollowUpResponse]] = None

    class Config:
        from_attributes = True


class ConfirmHandoverRequest(BaseModel):
    confirm_type: str  # handover, takeover
    signature: Optional[str] = None


@router.get("/shift-handovers", response_model=PaginatedResponse[ShiftHandoverResponse])
def get_shift_handovers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    shift_type: Optional[str] = None,
    status: Optional[str] = None,
    handover_person_name: Optional[str] = None,
    takeover_person_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ShiftHandover)
    if shift_type:
        query = query.filter(ShiftHandover.shift_type == shift_type)
    if status:
        query = query.filter(ShiftHandover.status == status)
    if handover_person_name:
        query = query.filter(ShiftHandover.handover_person_name.like(f"%{handover_person_name}%"))
    if takeover_person_name:
        query = query.filter(ShiftHandover.takeover_person_name.like(f"%{takeover_person_name}%"))
    if start_date:
        query = query.filter(ShiftHandover.shift_date >= start_date)
    if end_date:
        query = query.filter(ShiftHandover.shift_date <= end_date)

    total = query.count()
    items = query.order_by(ShiftHandover.shift_date.desc(), ShiftHandover.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/shift-handovers/{handover_id}", response_model=ShiftHandoverResponse)
def get_shift_handover(
    handover_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover = db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="交接班记录不存在")
    return handover


@router.post("/shift-handovers", response_model=ShiftHandoverResponse)
def create_shift_handover(
    handover_data: ShiftHandoverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover_no = f"SH{datetime.now().strftime('%Y%m%d%H%M%S')}"
    handover = ShiftHandover(
        handover_no=handover_no,
        shift_type=handover_data.shift_type,
        shift_date=handover_data.shift_date,
        start_time=handover_data.start_time,
        end_time=handover_data.end_time,
        handover_person_id=handover_data.handover_person_id,
        handover_person_name=handover_data.handover_person_name,
        takeover_person_id=handover_data.takeover_person_id,
        takeover_person_name=handover_data.takeover_person_name,
        water_volume_summary=handover_data.water_volume_summary,
        water_quality_summary=handover_data.water_quality_summary,
        equipment_status=handover_data.equipment_status,
        abnormal_notes=handover_data.abnormal_notes,
        remark=handover_data.remark,
        status="draft",
        created_by=current_user.id
    )

    if handover_data.follow_up_items:
        for item_data in handover_data.follow_up_items:
            follow_up = HandoverFollowUp(**item_data.model_dump())
            handover.follow_up_items.append(follow_up)

    db.add(handover)
    db.commit()
    db.refresh(handover)
    return handover


@router.put("/shift-handovers/{handover_id}", response_model=ShiftHandoverResponse)
def update_shift_handover(
    handover_id: int,
    handover_data: ShiftHandoverUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover = db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="交接班记录不存在")
    if handover.status in ("confirmed", "archived"):
        raise HTTPException(status_code=400, detail="已归档的交接班记录不可修改")

    update_data = handover_data.model_dump(exclude_unset=True, exclude={"follow_up_items"})
    for key, value in update_data.items():
        setattr(handover, key, value)

    if handover_data.follow_up_items is not None:
        existing_ids = {item.id for item in handover.follow_up_items if item.id}
        new_items = []
        for item_data in handover_data.follow_up_items:
            if item_data.id and item_data.id in existing_ids:
                existing_item = next((i for i in handover.follow_up_items if i.id == item_data.id), None)
                if existing_item:
                    item_dict = item_data.model_dump(exclude_unset=True)
                    for k, v in item_dict.items():
                        setattr(existing_item, k, v)
            else:
                item_dict = item_data.model_dump(exclude={"id"}, exclude_unset=True)
                new_items.append(HandoverFollowUp(**item_dict))
        handover.follow_up_items.extend(new_items)

    db.commit()
    db.refresh(handover)
    return handover


@router.delete("/shift-handovers/{handover_id}", response_model=MessageResponse)
def delete_shift_handover(
    handover_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover = db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="交接班记录不存在")
    if handover.status in ("confirmed", "archived"):
        raise HTTPException(status_code=400, detail="已归档的交接班记录不可删除")

    db.delete(handover)
    db.commit()
    return MessageResponse(message="删除成功")


@router.post("/shift-handovers/{handover_id}/confirm", response_model=ShiftHandoverResponse)
def confirm_shift_handover(
    handover_id: int,
    confirm_data: ConfirmHandoverRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover = db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="交接班记录不存在")
    if handover.status == "archived":
        raise HTTPException(status_code=400, detail="记录已归档")

    now = datetime.now()
    if confirm_data.confirm_type == "handover":
        handover.handover_confirm_time = now
        handover.handover_signature = confirm_data.signature or current_user.real_name or current_user.username
    elif confirm_data.confirm_type == "takeover":
        handover.takeover_confirm_time = now
        handover.takeover_signature = confirm_data.signature or current_user.real_name or current_user.username

    if handover.handover_confirm_time and handover.takeover_confirm_time:
        handover.status = "confirmed"
    elif handover.status == "draft":
        handover.status = "pending_confirm"

    db.commit()
    db.refresh(handover)
    return handover


@router.get("/shift-handovers/{handover_id}/follow-ups", response_model=List[HandoverFollowUpResponse])
def get_handover_follow_ups(
    handover_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover = db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="交接班记录不存在")
    return handover.follow_up_items


@router.post("/shift-handovers/{handover_id}/follow-ups", response_model=HandoverFollowUpResponse)
def create_handover_follow_up(
    handover_id: int,
    follow_up_data: HandoverFollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    handover = db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="交接班记录不存在")
    if handover.status in ("confirmed", "archived"):
        raise HTTPException(status_code=400, detail="已归档的交接班记录不可添加待办事项")

    follow_up = HandoverFollowUp(**follow_up_data.model_dump(), handover_id=handover_id)
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


@router.put("/shift-handovers/follow-ups/{follow_up_id}", response_model=HandoverFollowUpResponse)
def update_handover_follow_up(
    follow_up_id: int,
    follow_up_data: HandoverFollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    follow_up = db.query(HandoverFollowUp).filter(HandoverFollowUp.id == follow_up_id).first()
    if not follow_up:
        raise HTTPException(status_code=404, detail="待跟进事项不存在")

    update_data = follow_up_data.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(follow_up, key, value)

    if follow_up_data.status == "completed" and not follow_up.completed_time:
        follow_up.completed_time = datetime.now()

    db.commit()
    db.refresh(follow_up)
    return follow_up


@router.delete("/shift-handovers/follow-ups/{follow_up_id}", response_model=MessageResponse)
def delete_handover_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    follow_up = db.query(HandoverFollowUp).filter(HandoverFollowUp.id == follow_up_id).first()
    if not follow_up:
        raise HTTPException(status_code=404, detail="待跟进事项不存在")

    db.delete(follow_up)
    db.commit()
    return MessageResponse(message="删除成功")


# ================ 厂区电子地图 ================

class ZoneParameter(BaseModel):
    name: str
    code: str
    value: float
    unit: str
    standard: float
    min: Optional[float] = None
    max: Optional[float] = None
    status: str  # normal, warning, error


class ZoneAlarm(BaseModel):
    id: int
    title: str
    description: str
    level: str  # urgent, warning, normal
    time: datetime


class ZoneEquipment(BaseModel):
    id: int
    name: str
    type: str
    status: str  # running, standby, fault, maintenance


class ZoneStat(BaseModel):
    label: str
    value: str
    isWarning: bool = False


class ZoneData(BaseModel):
    id: str
    name: str
    x: int
    y: int
    width: int
    height: int
    color: str
    status: str  # normal, warning, error
    alarmCount: int
    equipmentRunning: int
    equipmentStandby: int
    equipmentFault: int
    equipmentTotal: int
    stats: List[ZoneStat]
    parameters: List[ZoneParameter]
    recentAlarms: List[ZoneAlarm]
    equipmentList: List[ZoneEquipment]


class FactoryMapResponse(BaseModel):
    zones: List[ZoneData]
    update_time: datetime


@router.get("/factory-map", response_model=FactoryMapResponse)
def get_factory_map_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.models.production import ProcessParameter, AbnormalAlarm
    from app.models.equipment import Equipment

    now = datetime.now()

    params = db.query(ProcessParameter).all()
    alarms = db.query(AbnormalAlarm).filter(AbnormalAlarm.status != "resolved").all()
    equipments = db.query(Equipment).all()

    def get_params_by_zone(zone_id: str) -> List[ZoneParameter]:
        zone_param_map = {
            "inlet": ["FLOW_IN", "COD_IN", "NH3N_IN", "PH_IN", "SS_IN", "TEMP"],
            "grating": ["GRATING_GAP", "GRATING_RESIDUE", "BELT_SPEED", "PRESSURE"],
            "biological": ["DO", "MLSS", "SV30", "SVI", "MIX_TEMP", "ORP", "INTERNAL_RATIO", "EXTERNAL_RATIO"],
            "secondary": ["SURFACE_LOAD", "WEIR_LOAD", "HRT", "SS_SEC", "SLUDGE_LEVEL"],
            "deep": ["TP_DEEP", "FILTER_HEAD", "FILTER_CYCLE", "BACKWASH_INT", "DOSAGE_PAC", "TURBIDITY"],
            "outlet": ["COD_OUT", "NH3N_OUT", "TP_OUT", "TN_OUT", "SS_OUT", "PH_OUT", "FLOW_OUT"]
        }
        param_codes = zone_param_map.get(zone_id, [])
        result = []
        for code in param_codes:
            param = next((p for p in params if p.code == code), None)
            if param:
                status = "normal"
                if param.current_value is not None and param.max_value is not None and param.current_value > param.max_value:
                    status = "warning" if param.current_value <= param.max_value * 1.1 else "error"
                result.append(ZoneParameter(
                    name=param.name,
                    code=param.code,
                    value=float(param.current_value or 0),
                    unit=param.unit or "",
                    standard=float(param.standard_value or 0),
                    min=float(param.min_value) if param.min_value else None,
                    max=float(param.max_value) if param.max_value else None,
                    status=status
                ))
        return result

    def get_alarms_by_zone(zone_id: str) -> List[ZoneAlarm]:
        zone_alarm_map = {
            "inlet": ["进水", "提升泵", "流量"],
            "grating": ["格栅", "栅渣", "压榨"],
            "biological": ["生化", "曝气", "溶解氧", "DO", "ORP", "MLSS"],
            "secondary": ["二沉", "沉淀", "污泥"],
            "deep": ["深度", "过滤", "反洗", "PAC", "除磷"],
            "outlet": ["出水", "排放", "COD", "氨氮"]
        }
        keywords = zone_alarm_map.get(zone_id, [])
        zone_alarms = []
        for alarm in alarms:
            if any(kw in (alarm.title or "") for kw in keywords) or any(kw in (alarm.description or "") for kw in keywords):
                level = alarm.alarm_level or "normal"
                if level not in ["urgent", "warning", "normal"]:
                    level = "normal"
                zone_alarms.append(ZoneAlarm(
                    id=alarm.id,
                    title=alarm.title,
                    description=alarm.description or "",
                    level=level,
                    time=alarm.alarm_time or now
                ))
        return zone_alarms[:3]

    def get_equipments_by_zone(zone_id: str) -> List[ZoneEquipment]:
        zone_equip_map = {
            "inlet": ["提升泵", "进水"],
            "grating": ["格栅", "输送机", "压榨机"],
            "biological": ["曝气", "搅拌器", "回流泵", "排泥泵"],
            "secondary": ["吸泥机", "刮泥机"],
            "deep": ["滤池", "反洗", "水泵", "风机", "计量泵"],
            "outlet": ["监测", "流量计", "消毒"]
        }
        keywords = zone_equip_map.get(zone_id, [])
        zone_equips = []
        for equip in equipments:
            equip_type = equip.process_section or equip.model or ""
            if any(kw in (equip.name or "") for kw in keywords) or any(kw in equip_type for kw in keywords):
                status = equip.status or "standby"
                if status not in ["running", "standby", "fault", "maintenance"]:
                    status = "standby"
                zone_equips.append(ZoneEquipment(
                    id=equip.id,
                    name=equip.name,
                    type=equip_type,
                    status=status
                ))
        return zone_equips[:10]

    zones_config = [
        {
            "id": "inlet",
            "name": "进水区",
            "x": 50, "y": 100, "width": 140, "height": 180,
            "color": "#e8f3ff"
        },
        {
            "id": "grating",
            "name": "格栅间",
            "x": 240, "y": 180, "width": 140, "height": 160,
            "color": "#e8ffea"
        },
        {
            "id": "biological",
            "name": "生化池",
            "x": 460, "y": 280, "width": 160, "height": 180,
            "color": "#fff7e8"
        },
        {
            "id": "secondary",
            "name": "二沉池",
            "x": 680, "y": 380, "width": 140, "height": 160,
            "color": "#f0f5ff"
        },
        {
            "id": "deep",
            "name": "深度处理",
            "x": 860, "y": 300, "width": 100, "height": 180,
            "color": "#ffe8e8"
        },
        {
            "id": "outlet",
            "name": "出水区",
            "x": 860, "y": 100, "width": 100, "height": 160,
            "color": "#e8fffc"
        }
    ]

    zones = []
    for config in zones_config:
        zone_parameters = get_params_by_zone(config["id"])
        zone_alarms_list = get_alarms_by_zone(config["id"])
        zone_equipments = get_equipments_by_zone(config["id"])

        has_error = any(p.status == "error" for p in zone_parameters) or any(a.level == "urgent" for a in zone_alarms_list)
        has_warning = any(p.status == "warning" for p in zone_parameters) or any(a.level == "warning" for a in zone_alarms_list)
        status = "error" if has_error else "warning" if has_warning else "normal"

        running = sum(1 for e in zone_equipments if e.status == "running")
        standby = sum(1 for e in zone_equipments if e.status == "standby")
        fault = sum(1 for e in zone_equipments if e.status == "fault")
        total = len(zone_equipments)

        stats = []
        if zone_parameters:
            for param in zone_parameters[:3]:
                stats.append(ZoneStat(
                    label=param.name,
                    value=f"{param.value} {param.unit}",
                    isWarning=param.status != "normal"
                ))

        zones.append(ZoneData(
            **config,
            status=status,
            alarmCount=len(zone_alarms_list),
            equipmentRunning=running,
            equipmentStandby=standby,
            equipmentFault=fault,
            equipmentTotal=total,
            stats=stats,
            parameters=zone_parameters,
            recentAlarms=zone_alarms_list,
            equipmentList=zone_equipments
        ))

    return FactoryMapResponse(
        zones=zones,
        update_time=now
    )


# =====================================================================
# 水质异常预警中心
# =====================================================================

class WaterQualityWarningItem(BaseModel):
    id: str
    warning_no: str
    indicator_type: str
    process_unit: str
    level: str  # urgent, warning, normal
    status: str  # pending, confirmed, processing, resolved
    measured_value: float
    limit_value: float
    unit: str
    deviation: float
    deviation_percent: float
    trigger_time: str
    duration: Optional[str] = None
    source: Optional[str] = "在线监测"
    device_name: Optional[str] = None
    confirmer: Optional[str] = None
    confirm_time: Optional[str] = None
    root_cause: Optional[str] = None
    handler: Optional[str] = None
    handle_description: Optional[str] = None
    snapshot_data: Optional[List[float]] = None


class IndicatorDistributionItem(BaseModel):
    name: str
    label: str
    count: int
    percent: int
    color: str


class WaterQualityStats(BaseModel):
    total: int
    pending: int
    processing: int
    resolved: int


class WaterQualityWarningsResponse(BaseModel):
    items: List[WaterQualityWarningItem]
    total: int
    stats: WaterQualityStats
    indicator_distribution: List[IndicatorDistributionItem]


# 模块级内存存储（首次访问时生成，跨请求保持状态）
_WQ_INDICATOR_META = {
    "COD": {"label": "COD", "unit": "mg/L", "color": "#165DFF", "limit": 50.0},
    "NH3N": {"label": "氨氮", "unit": "mg/L", "color": "#00b42a", "limit": 5.0},
    "TP": {"label": "总磷", "unit": "mg/L", "color": "#ff7d00", "limit": 0.5},
    "SS": {"label": "SS", "unit": "mg/L", "color": "#722ed1", "limit": 20.0},
    "TN": {"label": "总氮", "unit": "mg/L", "color": "#f53f3f", "limit": 15.0},
    "PH": {"label": "pH", "unit": "", "color": "#14c9c9", "limit": 6.5},
}

_WQ_PROCESS_UNITS = ["inlet", "biological", "secondary", "outlet"]
_WQ_DEVICE_MAP = {
    "COD": "COD分析仪",
    "NH3N": "氨氮在线仪",
    "TP": "总磷分析仪",
    "SS": "SS在线仪",
    "TN": "总氮分析仪",
    "PH": "pH计",
}

_WATER_QUALITY_WARNINGS: List[dict] = []


def _seed_water_quality_warnings():
    """根据当前日期生成一批确定性的水质预警数据"""
    global _WATER_QUALITY_WARNINGS
    if _WATER_QUALITY_WARNINGS:
        return

    from datetime import timedelta
    import random
    rng = random.Random(20240115)
    now = datetime.now()
    levels = ["urgent", "warning", "normal"]
    statuses = ["pending", "confirmed", "processing", "resolved"]
    root_causes = ["inlet_surge", "process_abnormal", "equipment_fault",
                   "dosage_insufficient", "sludge_issue", "other"]
    persons = ["张工", "李工", "王工", "赵工"]

    samples = []
    indicators = list(_WQ_INDICATOR_META.keys())
    for i in range(24):
        ind = indicators[i % len(indicators)]
        meta = _WQ_INDICATOR_META[ind]
        unit_proc = _WQ_PROCESS_UNITS[i % len(_WQ_PROCESS_UNITS)]
        limit = meta["limit"]
        ratio = rng.uniform(1.02, 1.35)
        measured = round(limit * ratio, 2)
        deviation = round(measured - limit, 2)
        deviation_percent = round(deviation / limit * 100, 1) if limit else 0
        trigger_dt = now - timedelta(hours=i * 3, minutes=rng.randint(0, 59))
        level = levels[0] if ratio > 1.2 else levels[1] if ratio > 1.08 else levels[2]
        status = statuses[i % len(statuses)]
        item = {
            "id": str(i + 1),
            "warning_no": f"WQW{trigger_dt.strftime('%Y%m%d')}{(i + 1):03d}",
            "indicator_type": ind,
            "process_unit": unit_proc,
            "level": level,
            "status": status,
            "measured_value": measured,
            "limit_value": limit,
            "unit": meta["unit"],
            "deviation": deviation,
            "deviation_percent": deviation_percent,
            "trigger_time": trigger_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{rng.randint(10, 120)}分钟",
            "source": "在线监测",
            "device_name": f"{unit_proc}-{_WQ_DEVICE_MAP[ind]}",
            "snapshot_data": [
                round(limit * 0.85, 2),
                round(limit * 0.92, 2),
                round(limit * 0.98, 2),
                measured,
                round(limit * 1.05, 2),
                round(limit * 1.0, 2),
                round(limit * 0.95, 2),
            ],
        }
        if status in ("confirmed", "processing", "resolved"):
            item["confirmer"] = rng.choice(persons)
            item["confirm_time"] = (trigger_dt + timedelta(minutes=15)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            item["root_cause"] = rng.choice(root_causes)
        if status in ("processing", "resolved"):
            item["handler"] = rng.choice(persons)
            item["handle_description"] = "已按工艺预案调整运行参数并加强巡检"
        samples.append(item)

    _WATER_QUALITY_WARNINGS = samples


@router.get("/water-quality-warnings", response_model=WaterQualityWarningsResponse)
def get_water_quality_warnings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    indicator_type: Optional[str] = None,
    process_unit: Optional[str] = None,
    status: Optional[str] = None,
    level: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    _seed_water_quality_warnings()
    data = list(_WATER_QUALITY_WARNINGS)

    if indicator_type:
        data = [d for d in data if d["indicator_type"] == indicator_type]
    if process_unit:
        data = [d for d in data if d["process_unit"] == process_unit]
    if status:
        data = [d for d in data if d["status"] == status]
    if level:
        data = [d for d in data if d["level"] == level]
    if start_time and end_time:
        data = [
            d for d in data
            if start_time <= d["trigger_time"] <= end_time
        ]

    total = len(data)
    start_idx = (page - 1) * page_size
    page_items = data[start_idx:start_idx + page_size]

    stats = WaterQualityStats(
        total=len(data),
        pending=sum(1 for d in data if d["status"] == "pending"),
        processing=sum(1 for d in data if d["status"] == "processing"),
        resolved=sum(1 for d in data if d["status"] == "resolved"),
    )

    counter: dict = {}
    for d in data:
        counter[d["indicator_type"]] = counter.get(d["indicator_type"], 0) + 1
    total_count = sum(counter.values()) or 1
    distribution = [
        IndicatorDistributionItem(
            name=name,
            label=_WQ_INDICATOR_META.get(name, {}).get("label", name),
            count=cnt,
            percent=round(cnt / total_count * 100),
            color=_WQ_INDICATOR_META.get(name, {}).get("color", "#165DFF"),
        )
        for name, cnt in counter.items()
    ]

    return WaterQualityWarningsResponse(
        items=[WaterQualityWarningItem(**d) for d in page_items],
        total=total,
        stats=stats,
        indicator_distribution=distribution,
    )


class WQConfirmRequest(BaseModel):
    confirm_result: str
    root_cause: Optional[str] = None
    remark: Optional[str] = None


@router.put("/water-quality-warnings/{warning_id}/confirm", response_model=MessageResponse)
def confirm_water_quality_warning(
    warning_id: str,
    payload: WQConfirmRequest,
    current_user: User = Depends(get_current_active_user),
):
    _seed_water_quality_warnings()
    for item in _WATER_QUALITY_WARNINGS:
        if item["id"] == warning_id:
            item["status"] = "confirmed"
            item["confirmer"] = current_user.username
            item["confirm_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if payload.confirm_result == "true_alarm" and payload.root_cause:
                item["root_cause"] = payload.root_cause
            return MessageResponse(message="确认成功")
    raise HTTPException(status_code=404, detail="预警记录不存在")


class WQHandleRequest(BaseModel):
    handle_status: str
    handle_description: str
    effect: Optional[str] = None


@router.put("/water-quality-warnings/{warning_id}/handle", response_model=MessageResponse)
def handle_water_quality_warning(
    warning_id: str,
    payload: WQHandleRequest,
    current_user: User = Depends(get_current_active_user),
):
    _seed_water_quality_warnings()
    for item in _WATER_QUALITY_WARNINGS:
        if item["id"] == warning_id:
            item["status"] = payload.handle_status
            item["handler"] = current_user.username
            item["handle_description"] = payload.handle_description
            return MessageResponse(message="处置记录已保存")
    raise HTTPException(status_code=404, detail="预警记录不存在")


@router.get("/water-quality-warnings/{warning_id}/snapshot")
def get_water_quality_warning_snapshot(
    warning_id: str,
    current_user: User = Depends(get_current_active_user),
):
    _seed_water_quality_warnings()
    for item in _WATER_QUALITY_WARNINGS:
        if item["id"] == warning_id:
            return {"data": item.get("snapshot_data", [])}
    raise HTTPException(status_code=404, detail="预警记录不存在")


@router.get("/water-quality-trend")
def get_water_quality_trend(
    indicator_type: Optional[str] = None,
    process_unit: Optional[str] = None,
    range: str = "6h",
    current_user: User = Depends(get_current_active_user),
):
    import math
    meta = _WQ_INDICATOR_META.get(indicator_type or "COD", _WQ_INDICATOR_META["COD"])
    limit = meta["limit"]
    config = {"1h": 12, "6h": 24, "24h": 24, "7d": 14}
    points = config.get(range, 24)
    times: List[str] = []
    values: List[float] = []
    for i in range(points):
        if range == "1h":
            times.append(f"{i * 5}分")
        elif range in ("6h", "24h"):
            hour = int(i * (0.25 if range == "6h" else 1))
            times.append(f"{hour:02d}:00")
        else:
            times.append(f"{i + 1}日")
        base = limit * 0.85
        variation = math.sin(i * 0.5) * limit * 0.15
        values.append(round(base + variation, 2))
    return {
        "times": times,
        "values": values,
        "limit": limit,
        "unit": meta["unit"],
    }


# =====================================================================
# 污泥清运调度台
# =====================================================================

class SludgeOrderItem(BaseModel):
    id: str
    order_no: str
    status: str
    sludge_property: str
    estimated_tonnage: float
    moisture_content: float
    vehicle_plate: Optional[str] = ""
    driver_name: Optional[str] = ""
    driver_phone: Optional[str] = ""
    destination: str
    planned_departure: Optional[str] = None
    planned_arrival: Optional[str] = None
    actual_departure: Optional[str] = ""
    actual_arrival: Optional[str] = ""
    created_at: Optional[str] = None
    dispatched_at: Optional[str] = None
    completed_at: Optional[str] = None
    remark: Optional[str] = ""


class PaginatedItems(BaseModel):
    items: List[dict]
    total: int


_SLUDGE_VEHICLES = [
    {"id": 1, "plate_number": "京A12345", "type": "自卸车", "load_capacity": 20},
    {"id": 2, "plate_number": "京B67890", "type": "密闭罐车", "load_capacity": 15},
    {"id": 3, "plate_number": "京C11111", "type": "自卸车", "load_capacity": 25},
    {"id": 4, "plate_number": "京D22222", "type": "自卸车", "load_capacity": 18},
    {"id": 5, "plate_number": "京E33333", "type": "密闭罐车", "load_capacity": 12},
]

_SLUDGE_DRIVERS = [
    {"id": 1, "name": "张师傅", "phone": "13800138001"},
    {"id": 2, "name": "李师傅", "phone": "13800138002"},
    {"id": 3, "name": "王师傅", "phone": "13800138003"},
    {"id": 4, "name": "赵师傅", "phone": "13800138004"},
    {"id": 5, "name": "刘师傅", "phone": "13800138005"},
]

_SLUDGE_DESTINATIONS = [
    {"id": 1, "name": "北京市污泥处置中心"},
    {"id": 2, "name": "通州污泥焚烧厂"},
    {"id": 3, "name": "大兴资源化利用基地"},
    {"id": 4, "name": "顺义污泥堆肥场"},
]

# 按日期分桶存储工单
_SLUDGE_ORDERS_BY_DATE: dict = {}
_SLUDGE_ORDER_SEQ = {"value": 1000}


def _build_seed_orders_for_date(date_str: str) -> List[dict]:
    """为指定日期生成一组确定性的污泥清运工单"""
    target = datetime.strptime(date_str, "%Y-%m-%d")
    base_no = target.strftime("%Y%m%d")
    properties = ["脱水污泥", "脱水污泥", "浓缩污泥", "脱水污泥", "消化污泥",
                  "脱水污泥", "剩余污泥", "脱水污泥"]
    statuses = ["pending", "dispatched", "transporting", "arrived",
                "completed", "pending", "transporting", "pending"]
    tonnages = [18.5, 22.0, 15.0, 20.0, 12.5, 25.0, 16.0, 18.0]
    moistures = [78, 80, 85, 76, 75, 77, 82, 79]
    destinations_pool = [d["name"] for d in _SLUDGE_DESTINATIONS]
    plan_departures = [(8, 30), (9, 0), (9, 30), (10, 0), (7, 0),
                       (13, 30), (11, 0), (15, 0)]
    plan_arrivals = [(9, 30), (10, 15), (10, 50), (11, 0), (8, 20),
                     (14, 45), (12, 20), (16, 0)]
    drivers_pool = [(v, d) for v, d in zip(_SLUDGE_VEHICLES, _SLUDGE_DRIVERS)]

    orders: List[dict] = []
    for idx in range(8):
        st = statuses[idx]
        veh, drv = drivers_pool[idx % len(drivers_pool)]
        pd = target.replace(hour=plan_departures[idx][0], minute=plan_departures[idx][1], second=0, microsecond=0)
        pa = target.replace(hour=plan_arrivals[idx][0], minute=plan_arrivals[idx][1], second=0, microsecond=0)
        order = {
            "id": f"{base_no}-{idx + 1}",
            "order_no": f"WN{base_no}{(idx + 1):03d}",
            "status": st,
            "sludge_property": properties[idx],
            "estimated_tonnage": tonnages[idx],
            "moisture_content": moistures[idx],
            "vehicle_plate": "" if st == "pending" else veh["plate_number"],
            "driver_name": "" if st == "pending" else drv["name"],
            "driver_phone": "" if st == "pending" else drv["phone"],
            "destination": destinations_pool[idx % len(destinations_pool)],
            "planned_departure": pd.strftime("%Y-%m-%d %H:%M:%S"),
            "planned_arrival": pa.strftime("%Y-%m-%d %H:%M:%S"),
            "actual_departure": "",
            "actual_arrival": "",
            "created_at": target.replace(hour=7, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S"),
            "dispatched_at": None,
            "completed_at": None,
            "remark": "",
        }
        if st in ("dispatched", "transporting", "arrived", "completed"):
            order["dispatched_at"] = (pd.replace(hour=max(pd.hour - 1, 0))
                                      .strftime("%Y-%m-%d %H:%M:%S"))
        if st in ("transporting", "arrived", "completed"):
            order["actual_departure"] = pd.strftime("%Y-%m-%d %H:%M:%S")
        if st in ("arrived", "completed"):
            order["actual_arrival"] = pa.strftime("%Y-%m-%d %H:%M:%S")
        if st == "completed":
            order["completed_at"] = (pa.replace(hour=min(pa.hour + 1, 23))
                                     .strftime("%Y-%m-%d %H:%M:%S"))
        orders.append(order)
    return orders


def _get_orders_for_date(date_str: str) -> List[dict]:
    if date_str not in _SLUDGE_ORDERS_BY_DATE:
        _SLUDGE_ORDERS_BY_DATE[date_str] = _build_seed_orders_for_date(date_str)
    return _SLUDGE_ORDERS_BY_DATE[date_str]


def _find_order(order_id: str) -> Optional[dict]:
    for orders in _SLUDGE_ORDERS_BY_DATE.values():
        for o in orders:
            if str(o["id"]) == str(order_id):
                return o
    return None


@router.get("/sludge-transport/orders")
def get_sludge_transport_orders(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    date_str = date or datetime.now().strftime("%Y-%m-%d")
    orders = _get_orders_for_date(date_str)
    return {"items": orders, "total": len(orders)}


@router.get("/sludge-transport/stats")
def get_sludge_transport_stats(
    current_user: User = Depends(get_current_active_user),
):
    date_str = datetime.now().strftime("%Y-%m-%d")
    orders = _get_orders_for_date(date_str)
    total = len(orders)
    return {
        "total": total,
        "pending": sum(1 for o in orders if o["status"] == "pending"),
        "dispatched": sum(1 for o in orders if o["status"] == "dispatched"),
        "transporting": sum(1 for o in orders if o["status"] == "transporting"),
        "arrived": sum(1 for o in orders if o["status"] == "arrived"),
        "completed": sum(1 for o in orders if o["status"] == "completed"),
        "totalTonnage": round(sum(o["estimated_tonnage"] for o in orders), 1),
    }


@router.get("/sludge-transport/vehicles")
def get_sludge_vehicles(
    current_user: User = Depends(get_current_active_user),
):
    return {"items": _SLUDGE_VEHICLES, "total": len(_SLUDGE_VEHICLES)}


@router.get("/sludge-transport/drivers")
def get_sludge_drivers(
    current_user: User = Depends(get_current_active_user),
):
    return {"items": _SLUDGE_DRIVERS, "total": len(_SLUDGE_DRIVERS)}


@router.get("/sludge-transport/destinations")
def get_sludge_destinations(
    current_user: User = Depends(get_current_active_user),
):
    return {"items": _SLUDGE_DESTINATIONS, "total": len(_SLUDGE_DESTINATIONS)}


class SludgeOrderCreate(BaseModel):
    sludge_property: str
    estimated_tonnage: float
    moisture_content: float
    destination: str
    planned_departure: Optional[str] = None
    planned_arrival: Optional[str] = None
    remark: Optional[str] = ""


@router.post("/sludge-transport/orders")
def create_sludge_transport_order(
    payload: SludgeOrderCreate,
    current_user: User = Depends(get_current_active_user),
):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    orders = _get_orders_for_date(date_str)
    _SLUDGE_ORDER_SEQ["value"] += 1
    seq = _SLUDGE_ORDER_SEQ["value"]
    order = {
        "id": f"{now.strftime('%Y%m%d')}-{seq}",
        "order_no": f"WN{now.strftime('%Y%m%d')}{seq:03d}",
        "status": "pending",
        "sludge_property": payload.sludge_property,
        "estimated_tonnage": payload.estimated_tonnage,
        "moisture_content": payload.moisture_content,
        "vehicle_plate": "",
        "driver_name": "",
        "driver_phone": "",
        "destination": payload.destination,
        "planned_departure": payload.planned_departure,
        "planned_arrival": payload.planned_arrival,
        "actual_departure": "",
        "actual_arrival": "",
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "dispatched_at": None,
        "completed_at": None,
        "remark": payload.remark or "",
    }
    orders.append(order)
    return order


@router.put("/sludge-transport/orders/{order_id}")
def update_sludge_transport_order(
    order_id: str,
    payload: SludgeOrderCreate,
    current_user: User = Depends(get_current_active_user),
):
    order = _find_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    order.update({
        "sludge_property": payload.sludge_property,
        "estimated_tonnage": payload.estimated_tonnage,
        "moisture_content": payload.moisture_content,
        "destination": payload.destination,
        "planned_departure": payload.planned_departure,
        "planned_arrival": payload.planned_arrival,
        "remark": payload.remark or "",
    })
    return order


class SludgeDispatchRequest(BaseModel):
    vehicle_id: int
    driver_id: int
    remark: Optional[str] = ""


@router.post("/sludge-transport/orders/{order_id}/dispatch")
def dispatch_sludge_transport_order(
    order_id: str,
    payload: SludgeDispatchRequest,
    current_user: User = Depends(get_current_active_user),
):
    order = _find_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    veh = next((v for v in _SLUDGE_VEHICLES if v["id"] == payload.vehicle_id), None)
    drv = next((d for d in _SLUDGE_DRIVERS if d["id"] == payload.driver_id), None)
    if not veh or not drv:
        raise HTTPException(status_code=400, detail="车辆或司机不存在")
    order["status"] = "dispatched"
    order["vehicle_plate"] = veh["plate_number"]
    order["driver_name"] = drv["name"]
    order["driver_phone"] = drv["phone"]
    order["dispatched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return order


class SludgeStatusUpdate(BaseModel):
    status: str


@router.put("/sludge-transport/orders/{order_id}/status")
def update_sludge_transport_status(
    order_id: str,
    payload: SludgeStatusUpdate,
    current_user: User = Depends(get_current_active_user),
):
    order = _find_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if payload.status not in ("pending", "dispatched", "transporting", "arrived", "completed"):
        raise HTTPException(status_code=400, detail="无效的状态值")
    order["status"] = payload.status
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if payload.status == "transporting":
        order["actual_departure"] = now_str
    elif payload.status == "arrived":
        order["actual_arrival"] = now_str
    elif payload.status == "completed":
        order["completed_at"] = now_str
    return order
