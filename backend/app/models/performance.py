from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class PerformanceIndicator(Base):
    """绩效考核指标"""
    __tablename__ = "performance_indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    category = Column(String(50))  # 生产、安全、质量等
    indicator_type = Column(String(30))  # quantitative, qualitative
    unit = Column(String(20))
    weight = Column(Float, default=1.0)  # 权重
    target_value = Column(Float)  # 目标值
    min_score = Column(Float, default=0)
    max_score = Column(Float, default=100)
    scoring_rules = Column(Text)  # 评分规则JSON
    data_source = Column(String(100))  # 数据来源
    is_auto_collect = Column(Boolean, default=False)  # 是否自动采集
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PerformanceData(Base):
    """绩效数据"""
    __tablename__ = "performance_data"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, nullable=False)
    user_id = Column(Integer)
    team_id = Column(Integer)  # 班组ID
    period_type = Column(String(20))  # daily, weekly, monthly
    period_date = Column(Date, nullable=False)
    actual_value = Column(Float)
    score = Column(Float)
    data_source = Column(String(30))  # auto, manual
    collector_id = Column(Integer)  # 采集人
    review_status = Column(String(20), default="pending")
    reviewer_id = Column(Integer)
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class PerformanceResult(Base):
    """绩效结果"""
    __tablename__ = "performance_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    user_name = Column(String(50))
    team_id = Column(Integer)
    team_name = Column(String(50))
    period_type = Column(String(20))  # monthly, quarterly, yearly
    period_start = Column(Date)
    period_end = Column(Date)
    total_score = Column(Float)
    rank = Column(Integer)  # 排名
    level = Column(String(10))  # A, B, C, D
    detail_scores = Column(Text)  # 各指标得分JSON
    reward_penalty = Column(Text)  # 奖惩记录JSON
    improvement_plan = Column(Text)  # 改进计划
    status = Column(String(20), default="draft")  # draft, confirmed
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
