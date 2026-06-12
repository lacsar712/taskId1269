from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class MaterialCategory(Base):
    """物资分类"""
    __tablename__ = "material_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    parent_id = Column(Integer, default=0)
    description = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class Material(Base):
    """物资台账"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer)
    specification = Column(String(100))  # 规格型号
    unit = Column(String(20))
    stock_quantity = Column(Float, default=0)
    min_stock = Column(Float, default=0)  # 库存下限
    max_stock = Column(Float, default=1000)  # 库存上限
    unit_price = Column(Float, default=0)
    warehouse_id = Column(Integer)  # 仓库ID
    location = Column(String(100))  # 库位
    supplier_id = Column(Integer)
    status = Column(String(20), default="normal")  # normal, low, out
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InboundRecord(Base):
    """入库记录"""
    __tablename__ = "inbound_records"

    id = Column(Integer, primary_key=True, index=True)
    inbound_no = Column(String(50), unique=True, nullable=False)
    inbound_type = Column(String(30))  # 采购入库、退货入库
    material_id = Column(Integer, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float)
    total_amount = Column(Float)
    supplier_id = Column(Integer)
    purchase_order_no = Column(String(50))
    warehouse_id = Column(Integer)
    operator_id = Column(Integer)
    operator_name = Column(String(50))
    inbound_date = Column(DateTime, nullable=False)
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class OutboundRecord(Base):
    """出库记录"""
    __tablename__ = "outbound_records"

    id = Column(Integer, primary_key=True, index=True)
    outbound_no = Column(String(50), unique=True, nullable=False)
    outbound_type = Column(String(30))  # 领用出库、报废出库
    material_id = Column(Integer, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float)
    total_amount = Column(Float)
    applicant_id = Column(Integer)
    applicant_name = Column(String(50))
    department = Column(String(50))
    purpose = Column(String(200))  # 用途
    warehouse_id = Column(Integer)
    operator_id = Column(Integer)
    operator_name = Column(String(50))
    outbound_date = Column(DateTime, nullable=False)
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Inventory(Base):
    """库存盘点"""
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    inventory_no = Column(String(50), unique=True, nullable=False)
    warehouse_id = Column(Integer)
    inventory_date = Column(Date, nullable=False)
    material_id = Column(Integer, nullable=False)
    system_quantity = Column(Float)  # 系统数量
    actual_quantity = Column(Float)  # 实际数量
    difference = Column(Float)  # 差异
    difference_reason = Column(Text)  # 差异原因
    handler_id = Column(Integer)
    handler_name = Column(String(50))
    status = Column(String(20), default="pending")  # pending, confirmed
    created_at = Column(DateTime, server_default=func.now())


class Supplier(Base):
    """供应商管理"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    contact_person = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    business_scope = Column(Text)  # 经营范围
    qualification = Column(Text)  # 资质证书
    rating = Column(String(10))  # 评级：A、B、C、D
    is_qualified = Column(Boolean, default=True)  # 是否合格供应商
    cooperation_start = Column(Date)
    remarks = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
