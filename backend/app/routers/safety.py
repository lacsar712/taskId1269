from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.safety import InspectionPlan, InspectionRecord, RiskPoint, EmergencyPlan, SafetyTraining, WorkPermit
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/safety", tags=["安全管理"])


# Schemas
class InspectionPlanResponse(BaseModel):
    id: int
    plan_no: str
    plan_name: str
    inspection_type: Optional[str]
    frequency: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InspectionPlanCreate(BaseModel):
    plan_name: str
    inspection_type: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class InspectionRecordResponse(BaseModel):
    id: int
    record_no: str
    inspector_name: Optional[str]
    inspection_date: datetime
    findings: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InspectionRecordCreate(BaseModel):
    plan_id: Optional[int] = None
    inspection_date: datetime
    check_points: Optional[str] = None
    findings: Optional[str] = None
    status: str = "normal"


class RiskPointResponse(BaseModel):
    id: int
    name: str
    code: str
    location: Optional[str]
    risk_type: Optional[str]
    risk_level: Optional[str]
    description: Optional[str]
    control_measures: Optional[str]
    responsible_person: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


class RiskPointCreate(BaseModel):
    name: str
    location: Optional[str] = None
    risk_type: Optional[str] = None
    risk_level: Optional[str] = None
    description: Optional[str] = None
    control_measures: Optional[str] = None
    responsible_person: Optional[str] = None


class EmergencyPlanResponse(BaseModel):
    id: int
    plan_no: str
    plan_name: str
    emergency_type: Optional[str]
    plan_level: Optional[str]
    drill_date: Optional[date]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SafetyTrainingResponse(BaseModel):
    id: int
    training_no: str
    title: str
    training_type: Optional[str]
    trainer: Optional[str]
    training_date: Optional[datetime]
    duration: Optional[int]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkPermitResponse(BaseModel):
    id: int
    permit_no: str
    work_type: str
    work_location: Optional[str]
    work_content: Optional[str]
    applicant_name: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    status: str
    approver_name: Optional[str]
    
    class Config:
        from_attributes = True


class WorkPermitCreate(BaseModel):
    work_type: str
    work_location: Optional[str] = None
    work_content: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    safety_measures: Optional[str] = None


# 安全巡检
@router.get("/inspections/plans", response_model=PaginatedResponse[InspectionPlanResponse])
def get_inspection_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(InspectionPlan)
    if status:
        query = query.filter(InspectionPlan.status == status)
    
    total = query.count()
    items = query.order_by(InspectionPlan.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/inspections/plans", response_model=InspectionPlanResponse)
def create_inspection_plan(
    data: InspectionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    plan_no = f"IP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    plan = InspectionPlan(
        plan_no=plan_no,
        plan_name=data.plan_name,
        inspection_type=data.inspection_type,
        frequency=data.frequency,
        route=data.route,
        start_date=data.start_date,
        end_date=data.end_date
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/inspections/records", response_model=PaginatedResponse[InspectionRecordResponse])
def get_inspection_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(InspectionRecord)
    if status:
        query = query.filter(InspectionRecord.status == status)
    
    total = query.count()
    items = query.order_by(InspectionRecord.inspection_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/inspections/records", response_model=InspectionRecordResponse)
def create_inspection_record(
    data: InspectionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    record_no = f"IR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record = InspectionRecord(
        plan_id=data.plan_id,
        record_no=record_no,
        inspector_id=current_user.id,
        inspector_name=current_user.real_name or current_user.username,
        inspection_date=data.inspection_date,
        check_points=data.check_points,
        findings=data.findings,
        status=data.status
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# 风险管控
@router.get("/risks", response_model=PaginatedResponse[RiskPointResponse])
def get_risk_points(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(RiskPoint)
    if risk_level:
        query = query.filter(RiskPoint.risk_level == risk_level)
    
    total = query.count()
    items = query.order_by(RiskPoint.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/risks", response_model=RiskPointResponse)
def create_risk_point(
    data: RiskPointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    code = f"RP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    risk = RiskPoint(
        name=data.name,
        code=code,
        location=data.location,
        risk_type=data.risk_type,
        risk_level=data.risk_level,
        description=data.description,
        control_measures=data.control_measures,
        responsible_person=data.responsible_person
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


# 应急管理
@router.get("/emergency/plans", response_model=List[EmergencyPlanResponse])
def get_emergency_plans(
    emergency_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(EmergencyPlan)
    if emergency_type:
        query = query.filter(EmergencyPlan.emergency_type == emergency_type)
    return query.all()


# 安全培训
@router.get("/trainings", response_model=PaginatedResponse[SafetyTrainingResponse])
def get_safety_trainings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(SafetyTraining)
    if status:
        query = query.filter(SafetyTraining.status == status)
    
    total = query.count()
    items = query.order_by(SafetyTraining.training_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 作业许可
@router.get("/permits", response_model=PaginatedResponse[WorkPermitResponse])
def get_work_permits(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(WorkPermit)
    if status:
        query = query.filter(WorkPermit.status == status)
    
    total = query.count()
    items = query.order_by(WorkPermit.apply_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/permits", response_model=WorkPermitResponse)
def create_work_permit(
    data: WorkPermitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    permit_no = f"WP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    permit = WorkPermit(
        permit_no=permit_no,
        work_type=data.work_type,
        work_location=data.work_location,
        work_content=data.work_content,
        applicant_id=current_user.id,
        applicant_name=current_user.real_name or current_user.username,
        start_time=data.start_time,
        end_time=data.end_time,
        safety_measures=data.safety_measures
    )
    db.add(permit)
    db.commit()
    db.refresh(permit)
    return permit


@router.put("/permits/{permit_id}/approve", response_model=MessageResponse)
def approve_work_permit(
    permit_id: int,
    approved: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    permit = db.query(WorkPermit).filter(WorkPermit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="许可不存在")
    
    permit.status = "approved" if approved else "rejected"
    permit.approver_id = current_user.id
    permit.approver_name = current_user.real_name or current_user.username
    permit.approve_time = datetime.now()
    db.commit()
    
    return MessageResponse(message="审批完成")
