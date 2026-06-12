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
            if any(kw in (equip.name or "") for kw in keywords) or any(kw in (equip.type or "") for kw in keywords):
                status = equip.status or "standby"
                if status not in ["running", "standby", "fault", "maintenance"]:
                    status = "standby"
                zone_equips.append(ZoneEquipment(
                    id=equip.id,
                    name=equip.name,
                    type=equip.type or "",
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
        parameters = get_params_by_zone(config["id"])
        alarms = get_alarms_by_zone(config["id"])
        equipments = get_equipments_by_zone(config["id"])

        has_error = any(p.status == "error" for p in parameters) or any(a.level == "urgent" for a in alarms)
        has_warning = any(p.status == "warning" for p in parameters) or any(a.level == "warning" for a in alarms)
        status = "error" if has_error else "warning" if has_warning else "normal"

        running = sum(1 for e in equipments if e.status == "running")
        standby = sum(1 for e in equipments if e.status == "standby")
        fault = sum(1 for e in equipments if e.status == "fault")
        total = len(equipments)

        stats = []
        if parameters:
            for param in parameters[:3]:
                stats.append(ZoneStat(
                    label=param.name,
                    value=f"{param.value} {param.unit}",
                    isWarning=param.status != "normal"
                ))

        zones.append(ZoneData(
            **config,
            status=status,
            alarmCount=len(alarms),
            equipmentRunning=running,
            equipmentStandby=standby,
            equipmentFault=fault,
            equipmentTotal=total,
            stats=stats,
            parameters=parameters,
            recentAlarms=alarms,
            equipmentList=equipments
        ))

    return FactoryMapResponse(
        zones=zones,
        update_time=now
    )
