from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class AlarmLevel(str, enum.Enum):
    NORMAL = "normal"
    WARNING = "warning"
    URGENT = "urgent"


class AlarmStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"


class ProcessParameter(Base):
    """工艺参数实时监控"""
    __tablename__ = "process_parameters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    unit = Column(String(20))
    current_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    standard_value = Column(Float)
    process_section = Column(String(50))  # 工艺段
    equipment_id = Column(Integer)
    status = Column(String(20), default="normal")
    recorded_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())


class ProductionPlan(Base):
    """生产计划"""
    __tablename__ = "production_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    plan_date = Column(DateTime, nullable=False)
    target_volume = Column(Float)  # 目标处理量
    actual_volume = Column(Float)  # 实际处理量
    operation_mode = Column(String(50))  # 工况模式
    description = Column(Text)
    status = Column(String(20), default="pending")  # pending, executing, completed
    created_by = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ProductionLog(Base):
    """生产日志"""
    __tablename__ = "production_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(DateTime, nullable=False)
    shift = Column(String(20))  # 班次：早班、中班、晚班
    log_type = Column(String(30))  # auto, manual, handover
    content = Column(Text, nullable=False)
    operator_id = Column(Integer)
    operator_name = Column(String(50))
    attachment = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class AbnormalAlarm(Base):
    """异常告警"""
    __tablename__ = "abnormal_alarms"

    id = Column(Integer, primary_key=True, index=True)
    alarm_no = Column(String(50), unique=True, nullable=False)
    alarm_type = Column(String(50), nullable=False)  # 水质超标、工艺参数异常、工况异常
    alarm_level = Column(String(20), default="normal")
    title = Column(String(200), nullable=False)
    description = Column(Text)
    source = Column(String(100))  # 告警来源
    related_param = Column(String(50))  # 关联参数
    current_value = Column(Float)
    threshold_value = Column(Float)
    status = Column(String(20), default="pending")
    handler_id = Column(Integer)
    handler_name = Column(String(50))
    handle_time = Column(DateTime)
    handle_result = Column(Text)
    alarm_time = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())


class ProcessOptimization(Base):
    """工艺优化建议"""
    __tablename__ = "process_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    optimization_type = Column(String(50))  # 智能调节、效率分析、模拟仿真
    current_situation = Column(Text)
    suggestion = Column(Text, nullable=False)
    expected_effect = Column(Text)
    priority = Column(Integer, default=1)
    status = Column(String(20), default="pending")  # pending, approved, implemented
    created_by = Column(Integer)
    approved_by = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
