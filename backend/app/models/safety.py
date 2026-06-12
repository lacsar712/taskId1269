from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class InspectionPlan(Base):
    """巡检计划"""
    __tablename__ = "inspection_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    inspection_type = Column(String(50))  # 日常巡检、专项巡检
    frequency = Column(String(30))  # daily, weekly, monthly
    route = Column(Text)  # 巡检路线JSON
    inspector_ids = Column(Text)  # 巡检人员ID列表
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InspectionRecord(Base):
    """巡检记录"""
    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer)
    record_no = Column(String(50), unique=True, nullable=False)
    inspector_id = Column(Integer)
    inspector_name = Column(String(50))
    inspection_date = Column(DateTime, nullable=False)
    check_points = Column(Text)  # 检查点位JSON
    findings = Column(Text)  # 发现问题
    status = Column(String(20), default="normal")  # normal, abnormal
    images = Column(Text)  # 图片路径JSON
    created_at = Column(DateTime, server_default=func.now())


class RiskPoint(Base):
    """风险点台账"""
    __tablename__ = "risk_points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    location = Column(String(200))
    risk_type = Column(String(50))  # 设备风险、环境风险、操作风险
    risk_level = Column(String(20))  # low, medium, high, critical
    description = Column(Text)
    control_measures = Column(Text)
    responsible_person = Column(String(50))
    assessment_date = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmergencyPlan(Base):
    """应急预案"""
    __tablename__ = "emergency_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    emergency_type = Column(String(50))  # 环境事故、安全事故、设备故障
    plan_level = Column(String(20))  # 一级、二级、三级
    content = Column(Text, nullable=False)
    response_team = Column(Text)  # 响应团队JSON
    resources = Column(Text)  # 应急资源JSON
    drill_date = Column(Date)  # 最近演练日期
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SafetyTraining(Base):
    """安全培训"""
    __tablename__ = "safety_trainings"

    id = Column(Integer, primary_key=True, index=True)
    training_no = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    training_type = Column(String(50))  # 入职培训、专项培训、复训
    trainer = Column(String(50))
    training_date = Column(DateTime)
    duration = Column(Integer)  # 培训时长(小时)
    participants = Column(Text)  # 参训人员JSON
    content = Column(Text)
    materials = Column(Text)  # 培训材料路径
    status = Column(String(20), default="planned")
    created_at = Column(DateTime, server_default=func.now())


class WorkPermit(Base):
    """作业许可"""
    __tablename__ = "work_permits"

    id = Column(Integer, primary_key=True, index=True)
    permit_no = Column(String(50), unique=True, nullable=False)
    work_type = Column(String(50), nullable=False)  # 动火作业、受限空间、高处作业
    work_location = Column(String(200))
    work_content = Column(Text)
    applicant_id = Column(Integer)
    applicant_name = Column(String(50))
    apply_time = Column(DateTime, server_default=func.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    safety_measures = Column(Text)
    approver_id = Column(Integer)
    approver_name = Column(String(50))
    approve_time = Column(DateTime)
    status = Column(String(20), default="pending")  # pending, approved, rejected, completed
    created_at = Column(DateTime, server_default=func.now())
