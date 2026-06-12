from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class Sample(Base):
    """样品管理"""
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_no = Column(String(50), unique=True, nullable=False)
    sample_name = Column(String(100), nullable=False)
    sample_type = Column(String(50))  # 进水、出水、过程水
    sampling_point = Column(String(100))  # 采样点
    sampling_time = Column(DateTime, nullable=False)
    sampler_id = Column(Integer)
    sampler_name = Column(String(50))
    sample_volume = Column(Float)  # 样品量
    storage_condition = Column(String(100))  # 保存条件
    storage_location = Column(String(100))  # 存放位置
    expiry_date = Column(DateTime)  # 有效期
    status = Column(String(20), default="registered")  # registered, testing, completed, expired
    created_at = Column(DateTime, server_default=func.now())


class DetectionTask(Base):
    """检测任务"""
    __tablename__ = "detection_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_no = Column(String(50), unique=True, nullable=False)
    sample_id = Column(Integer)
    detection_items = Column(Text)  # 检测项目JSON
    priority = Column(String(20), default="normal")  # urgent, normal, low
    assigned_to = Column(Integer)  # 指派检测员
    assigned_name = Column(String(50))
    due_date = Column(DateTime)
    status = Column(String(20), default="pending")  # pending, testing, completed
    progress = Column(Integer, default=0)  # 进度百分比
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DetectionData(Base):
    """检测数据"""
    __tablename__ = "detection_data"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer)
    sample_id = Column(Integer)
    parameter_name = Column(String(50), nullable=False)  # 检测参数
    parameter_code = Column(String(30))
    detection_method = Column(String(100))  # 检测方法
    detection_value = Column(Float)
    unit = Column(String(20))
    standard_min = Column(Float)  # 标准下限
    standard_max = Column(Float)  # 标准上限
    is_qualified = Column(Boolean, default=True)
    is_abnormal = Column(Boolean, default=False)
    detector_id = Column(Integer)
    detector_name = Column(String(50))
    detection_time = Column(DateTime)
    reviewer_id = Column(Integer)  # 审核人
    review_status = Column(String(20), default="pending")
    created_at = Column(DateTime, server_default=func.now())


class DetectionReport(Base):
    """检测报告"""
    __tablename__ = "detection_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_no = Column(String(50), unique=True, nullable=False)
    task_id = Column(Integer)
    sample_id = Column(Integer)
    report_title = Column(String(200))
    report_content = Column(Text)
    conclusion = Column(Text)
    prepared_by = Column(Integer)
    prepared_name = Column(String(50))
    reviewed_by = Column(Integer)
    reviewed_name = Column(String(50))
    approved_by = Column(Integer)
    approved_name = Column(String(50))
    status = Column(String(20), default="draft")  # draft, reviewing, approved, archived
    file_path = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class QualityControl(Base):
    """质控管理"""
    __tablename__ = "quality_controls"

    id = Column(Integer, primary_key=True, index=True)
    qc_type = Column(String(50), nullable=False)  # 标样、空白试验、平行试验
    qc_no = Column(String(50), unique=True, nullable=False)
    parameter_name = Column(String(50))
    standard_value = Column(Float)
    measured_value = Column(Float)
    deviation = Column(Float)  # 偏差
    is_qualified = Column(Boolean)
    instrument_id = Column(Integer)  # 仪器ID
    instrument_name = Column(String(100))
    executor_id = Column(Integer)
    executor_name = Column(String(50))
    execute_time = Column(DateTime)
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Standard(Base):
    """标准库"""
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    standard_type = Column(String(50), nullable=False)  # 检测方法、限值标准
    standard_no = Column(String(50), unique=True, nullable=False)
    standard_name = Column(String(200), nullable=False)
    parameter_name = Column(String(50))
    limit_min = Column(Float)
    limit_max = Column(Float)
    unit = Column(String(20))
    applicable_scope = Column(String(200))  # 适用范围
    effective_date = Column(Date)
    status = Column(String(20), default="active")
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
