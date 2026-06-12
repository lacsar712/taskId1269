from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.equipment import Equipment, EquipmentCategory, MaintenancePlan, MaintenanceRecord, Fault, SparePart
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/equipment", tags=["设备管理"])


# Schemas
class EquipmentCategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    parent_id: int
    description: Optional[str]
    
    class Config:
        from_attributes = True


class EquipmentResponse(BaseModel):
    id: int
    name: str
    code: str
    category_id: Optional[int]
    model: Optional[str]
    manufacturer: Optional[str]
    location: Optional[str]
    process_section: Optional[str]
    status: str
    running_hours: Optional[float]
    last_maintenance_date: Optional[date]
    next_maintenance_date: Optional[date]
    responsible_person: Optional[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EquipmentCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    install_date: Optional[date] = None
    location: Optional[str] = None
    process_section: Optional[str] = None
    rated_power: Optional[float] = None
    responsible_person: Optional[str] = None


class MaintenancePlanResponse(BaseModel):
    id: int
    plan_no: str
    equipment_id: int
    maintenance_type: Optional[str]
    frequency: Optional[str]
    content: Optional[str]
    next_date: Optional[date]
    status: str
    
    class Config:
        from_attributes = True


class MaintenanceRecordResponse(BaseModel):
    id: int
    record_no: str
    equipment_id: int
    maintenance_type: Optional[str]
    maintenance_date: datetime
    content: Optional[str]
    cost: Optional[float]
    executor_name: Optional[str]
    result: str
    
    class Config:
        from_attributes = True


class FaultResponse(BaseModel):
    id: int
    fault_no: str
    equipment_id: int
    fault_type: Optional[str]
    fault_level: Optional[str]
    description: str
    fault_time: datetime
    status: str
    repairer_name: Optional[str]
    
    class Config:
        from_attributes = True


class FaultCreate(BaseModel):
    equipment_id: int
    fault_type: Optional[str] = None
    fault_level: Optional[str] = None
    description: str
    fault_time: datetime


class SparePartResponse(BaseModel):
    id: int
    name: str
    code: str
    model: Optional[str]
    category: Optional[str]
    unit: Optional[str]
    stock_quantity: int
    min_stock: int
    max_stock: int
    location: Optional[str]
    unit_price: Optional[float]
    status: str
    
    class Config:
        from_attributes = True


# 设备分类
@router.get("/categories", response_model=List[EquipmentCategoryResponse])
def get_equipment_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(EquipmentCategory).all()


# 设备台账
@router.get("", response_model=PaginatedResponse[EquipmentResponse])
def get_equipments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Equipment)
    if category_id:
        query = query.filter(Equipment.category_id == category_id)
    if status:
        query = query.filter(Equipment.status == status)
    if keyword:
        query = query.filter(
            (Equipment.name.contains(keyword)) |
            (Equipment.code.contains(keyword))
        )
    
    total = query.count()
    items = query.order_by(Equipment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=EquipmentResponse)
def create_equipment(
    data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    code = f"EQ{datetime.now().strftime('%Y%m%d%H%M%S')}"
    equipment = Equipment(
        name=data.name,
        code=code,
        category_id=data.category_id,
        model=data.model,
        manufacturer=data.manufacturer,
        purchase_date=data.purchase_date,
        install_date=data.install_date,
        location=data.location,
        process_section=data.process_section,
        rated_power=data.rated_power,
        responsible_person=data.responsible_person
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    return equipment


# 维护保养
@router.get("/maintenance/plans", response_model=PaginatedResponse[MaintenancePlanResponse])
def get_maintenance_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    equipment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(MaintenancePlan)
    if equipment_id:
        query = query.filter(MaintenancePlan.equipment_id == equipment_id)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/maintenance/records", response_model=PaginatedResponse[MaintenanceRecordResponse])
def get_maintenance_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    equipment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(MaintenanceRecord)
    if equipment_id:
        query = query.filter(MaintenanceRecord.equipment_id == equipment_id)
    
    total = query.count()
    items = query.order_by(MaintenanceRecord.maintenance_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 故障管理
@router.get("/faults", response_model=PaginatedResponse[FaultResponse])
def get_faults(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    fault_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Fault)
    if status:
        query = query.filter(Fault.status == status)
    if fault_level:
        query = query.filter(Fault.fault_level == fault_level)
    
    total = query.count()
    items = query.order_by(Fault.fault_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/faults", response_model=FaultResponse)
def create_fault(
    data: FaultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    fault_no = f"FT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    fault = Fault(
        fault_no=fault_no,
        equipment_id=data.equipment_id,
        fault_type=data.fault_type,
        fault_level=data.fault_level,
        description=data.description,
        fault_time=data.fault_time
    )
    db.add(fault)
    db.commit()
    db.refresh(fault)
    return fault


# 备件管理
@router.get("/spareparts", response_model=PaginatedResponse[SparePartResponse])
def get_spare_parts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(SparePart)
    if keyword:
        query = query.filter(
            (SparePart.name.contains(keyword)) |
            (SparePart.code.contains(keyword))
        )
    if status:
        query = query.filter(SparePart.status == status)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
