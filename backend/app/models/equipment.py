from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class EquipmentCategory(Base):
    """设备分类"""
    __tablename__ = "equipment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    parent_id = Column(Integer, default=0)
    description = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class Equipment(Base):
    """设备台账"""
    __tablename__ = "equipments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer)
    model = Column(String(100))  # 型号规格
    manufacturer = Column(String(100))  # 生产厂家
    purchase_date = Column(Date)
    install_date = Column(Date)
    location = Column(String(200))  # 安装位置
    process_section = Column(String(50))  # 所属工艺段
    rated_power = Column(Float)  # 额定功率
    status = Column(String(20), default="running")  # running, stopped, maintenance, fault
    running_hours = Column(Float, default=0)  # 累计运行时长
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    responsible_person = Column(String(50))
    qr_code = Column(String(200))  # 二维码
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MaintenancePlan(Base):
    """维护保养计划"""
    __tablename__ = "maintenance_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    equipment_id = Column(Integer, nullable=False)
    maintenance_type = Column(String(30))  # 日常保养、定期保养、大修
    frequency = Column(String(30))  # daily, weekly, monthly, quarterly, yearly
    content = Column(Text)
    next_date = Column(Date)
    reminder_days = Column(Integer, default=3)  # 提前提醒天数
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())


class MaintenanceRecord(Base):
    """维护保养记录"""
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    record_no = Column(String(50), unique=True, nullable=False)
    plan_id = Column(Integer)
    equipment_id = Column(Integer, nullable=False)
    maintenance_type = Column(String(30))
    maintenance_date = Column(DateTime, nullable=False)
    content = Column(Text)
    parts_replaced = Column(Text)  # 更换配件JSON
    cost = Column(Float, default=0)
    executor_id = Column(Integer)
    executor_name = Column(String(50))
    result = Column(String(20), default="completed")
    images = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Fault(Base):
    """故障记录"""
    __tablename__ = "faults"

    id = Column(Integer, primary_key=True, index=True)
    fault_no = Column(String(50), unique=True, nullable=False)
    equipment_id = Column(Integer, nullable=False)
    fault_type = Column(String(50))  # 设备故障、参数超限、维保到期
    fault_level = Column(String(20))  # minor, major, critical
    description = Column(Text, nullable=False)
    fault_time = Column(DateTime, nullable=False)
    repair_start = Column(DateTime)
    repair_end = Column(DateTime)
    repair_content = Column(Text)
    parts_used = Column(Text)  # 使用配件JSON
    repair_cost = Column(Float, default=0)
    repairer_id = Column(Integer)
    repairer_name = Column(String(50))
    status = Column(String(20), default="pending")  # pending, repairing, completed
    cause_analysis = Column(Text)  # 故障原因分析
    preventive_measures = Column(Text)  # 预防措施
    created_at = Column(DateTime, server_default=func.now())


class SparePart(Base):
    """备件管理"""
    __tablename__ = "spare_parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    model = Column(String(100))  # 规格型号
    category = Column(String(50))  # 分类
    unit = Column(String(20))  # 单位
    stock_quantity = Column(Integer, default=0)  # 库存数量
    min_stock = Column(Integer, default=0)  # 最小库存
    max_stock = Column(Integer, default=100)  # 最大库存
    location = Column(String(100))  # 存放位置
    applicable_equipment = Column(Text)  # 适用设备JSON
    supplier = Column(String(100))
    unit_price = Column(Float, default=0)
    status = Column(String(20), default="normal")  # normal, low, out
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
