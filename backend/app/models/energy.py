from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class EnergyData(Base):
    """能耗数据"""
    __tablename__ = "energy_data"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(50), nullable=False)  # electricity, water, gas
    equipment_id = Column(Integer)
    process_section = Column(String(50))  # 工艺段
    meter_id = Column(String(50))  # 计量表编号
    reading_value = Column(Float)
    consumption = Column(Float)  # 消耗量
    unit = Column(String(20))
    unit_cost = Column(Float)  # 单价
    total_cost = Column(Float)  # 总费用
    record_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="normal")  # normal, abnormal
    created_at = Column(DateTime, server_default=func.now())


class EnergySavingPlan(Base):
    """节能方案"""
    __tablename__ = "energy_saving_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    plan_type = Column(String(50))  # 智能建议、人工制定
    target_section = Column(String(50))  # 目标工艺段
    current_consumption = Column(Float)  # 当前能耗
    target_consumption = Column(Float)  # 目标能耗
    saving_rate = Column(Float)  # 节能率
    measures = Column(Text)  # 节能措施JSON
    start_date = Column(Date)
    end_date = Column(Date)
    actual_saving = Column(Float)  # 实际节能量
    status = Column(String(20), default="planned")  # planned, executing, completed, evaluated
    created_by = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EnergyCost(Base):
    """能耗成本"""
    __tablename__ = "energy_costs"

    id = Column(Integer, primary_key=True, index=True)
    cost_date = Column(Date, nullable=False)
    cost_type = Column(String(50))  # electricity, water, gas, total
    department = Column(String(50))  # 部门/工艺段
    consumption = Column(Float)  # 消耗量
    unit_price = Column(Float)  # 单价
    total_cost = Column(Float)  # 总成本
    allocated_cost = Column(Float)  # 分摊成本
    budget = Column(Float)  # 预算
    variance = Column(Float)  # 差异
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
