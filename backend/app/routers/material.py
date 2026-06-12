from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.material import Material, MaterialCategory, InboundRecord, OutboundRecord, Inventory, Supplier
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/materials", tags=["物资管理"])


# Schemas
class MaterialCategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    parent_id: int
    description: Optional[str]
    
    class Config:
        from_attributes = True


class MaterialResponse(BaseModel):
    id: int
    name: str
    code: str
    category_id: Optional[int]
    specification: Optional[str]
    unit: Optional[str]
    stock_quantity: float
    min_stock: float
    max_stock: float
    unit_price: float
    location: Optional[str]
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MaterialCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    min_stock: float = 0
    max_stock: float = 1000
    unit_price: float = 0
    warehouse_id: Optional[int] = None
    location: Optional[str] = None
    supplier_id: Optional[int] = None


class InboundRecordResponse(BaseModel):
    id: int
    inbound_no: str
    inbound_type: Optional[str]
    material_id: int
    quantity: float
    unit_price: Optional[float]
    total_amount: Optional[float]
    operator_name: Optional[str]
    inbound_date: datetime
    remarks: Optional[str]
    
    class Config:
        from_attributes = True


class InboundCreate(BaseModel):
    inbound_type: str
    material_id: int
    quantity: float
    unit_price: Optional[float] = None
    supplier_id: Optional[int] = None
    purchase_order_no: Optional[str] = None
    warehouse_id: Optional[int] = None
    remarks: Optional[str] = None


class OutboundRecordResponse(BaseModel):
    id: int
    outbound_no: str
    outbound_type: Optional[str]
    material_id: int
    quantity: float
    unit_price: Optional[float]
    total_amount: Optional[float]
    applicant_name: Optional[str]
    department: Optional[str]
    purpose: Optional[str]
    operator_name: Optional[str]
    outbound_date: datetime
    
    class Config:
        from_attributes = True


class OutboundCreate(BaseModel):
    outbound_type: str
    material_id: int
    quantity: float
    department: Optional[str] = None
    purpose: Optional[str] = None
    warehouse_id: Optional[int] = None
    remarks: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    code: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    rating: Optional[str]
    is_qualified: bool
    status: str
    
    class Config:
        from_attributes = True


# 物资分类
@router.get("/categories", response_model=List[MaterialCategoryResponse])
def get_material_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(MaterialCategory).all()


# 物资台账
@router.get("", response_model=PaginatedResponse[MaterialResponse])
def get_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Material)
    if category_id:
        query = query.filter(Material.category_id == category_id)
    if keyword:
        query = query.filter(
            (Material.name.contains(keyword)) |
            (Material.code.contains(keyword))
        )
    if status:
        query = query.filter(Material.status == status)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=MaterialResponse)
def create_material(
    data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    code = f"MT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    material = Material(
        name=data.name,
        code=code,
        category_id=data.category_id,
        specification=data.specification,
        unit=data.unit,
        min_stock=data.min_stock,
        max_stock=data.max_stock,
        unit_price=data.unit_price,
        warehouse_id=data.warehouse_id,
        location=data.location,
        supplier_id=data.supplier_id
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


# 入库管理
@router.get("/inbound", response_model=PaginatedResponse[InboundRecordResponse])
def get_inbound_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    inbound_type: Optional[str] = None,
    material_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(InboundRecord)
    if inbound_type:
        query = query.filter(InboundRecord.inbound_type == inbound_type)
    if material_id:
        query = query.filter(InboundRecord.material_id == material_id)
    
    total = query.count()
    items = query.order_by(InboundRecord.inbound_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/inbound", response_model=InboundRecordResponse)
def create_inbound(
    data: InboundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    material = db.query(Material).filter(Material.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物资不存在")
    
    inbound_no = f"IN{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_amount = (data.unit_price or material.unit_price) * data.quantity
    
    record = InboundRecord(
        inbound_no=inbound_no,
        inbound_type=data.inbound_type,
        material_id=data.material_id,
        quantity=data.quantity,
        unit_price=data.unit_price or material.unit_price,
        total_amount=total_amount,
        supplier_id=data.supplier_id,
        purchase_order_no=data.purchase_order_no,
        warehouse_id=data.warehouse_id,
        operator_id=current_user.id,
        operator_name=current_user.real_name or current_user.username,
        inbound_date=datetime.now(),
        remarks=data.remarks
    )
    db.add(record)
    
    # 更新库存
    material.stock_quantity += data.quantity
    if material.stock_quantity < material.min_stock:
        material.status = "low"
    else:
        material.status = "normal"
    
    db.commit()
    db.refresh(record)
    return record


# 出库管理
@router.get("/outbound", response_model=PaginatedResponse[OutboundRecordResponse])
def get_outbound_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    outbound_type: Optional[str] = None,
    material_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(OutboundRecord)
    if outbound_type:
        query = query.filter(OutboundRecord.outbound_type == outbound_type)
    if material_id:
        query = query.filter(OutboundRecord.material_id == material_id)
    
    total = query.count()
    items = query.order_by(OutboundRecord.outbound_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/outbound", response_model=OutboundRecordResponse)
def create_outbound(
    data: OutboundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    material = db.query(Material).filter(Material.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物资不存在")
    
    if material.stock_quantity < data.quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    
    outbound_no = f"OUT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_amount = material.unit_price * data.quantity
    
    record = OutboundRecord(
        outbound_no=outbound_no,
        outbound_type=data.outbound_type,
        material_id=data.material_id,
        quantity=data.quantity,
        unit_price=material.unit_price,
        total_amount=total_amount,
        applicant_id=current_user.id,
        applicant_name=current_user.real_name or current_user.username,
        department=data.department,
        purpose=data.purpose,
        warehouse_id=data.warehouse_id,
        operator_id=current_user.id,
        operator_name=current_user.real_name or current_user.username,
        outbound_date=datetime.now(),
        remarks=data.remarks
    )
    db.add(record)
    
    # 更新库存
    material.stock_quantity -= data.quantity
    if material.stock_quantity <= 0:
        material.status = "out"
    elif material.stock_quantity < material.min_stock:
        material.status = "low"
    
    db.commit()
    db.refresh(record)
    return record


# 供应商管理
@router.get("/suppliers", response_model=PaginatedResponse[SupplierResponse])
def get_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_qualified: Optional[bool] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Supplier)
    if is_qualified is not None:
        query = query.filter(Supplier.is_qualified == is_qualified)
    if keyword:
        query = query.filter(
            (Supplier.name.contains(keyword)) |
            (Supplier.code.contains(keyword))
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
