from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from app.database import Base


class ReportTemplate(Base):
    """报表模板"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    report_type = Column(String(50))  # 日报、月报、季报、年报、环保报表
    category = Column(String(50))  # 生产、能耗、设备等
    content_config = Column(Text)  # 报表内容配置JSON
    layout_config = Column(Text)  # 布局配置JSON
    data_source = Column(Text)  # 数据源配置JSON
    permissions = Column(Text)  # 权限配置JSON
    status = Column(String(20), default="active")
    created_by = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CustomReport(Base):
    """自定义报表"""
    __tablename__ = "custom_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_no = Column(String(50), unique=True, nullable=False)
    report_name = Column(String(100), nullable=False)
    template_id = Column(Integer)
    report_date = Column(Date, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    content = Column(Text)  # 报表内容JSON
    summary = Column(Text)  # 报表摘要
    status = Column(String(20), default="draft")  # draft, final, archived
    created_by = Column(Integer)
    created_name = Column(String(50))
    approved_by = Column(Integer)
    approved_name = Column(String(50))
    file_path = Column(String(200))
    modify_log = Column(Text)  # 修改日志JSON
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
