from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class SystemConfig(Base):
    """系统配置"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    config_type = Column(String(30))  # alarm, report, interface, other
    description = Column(String(200))
    is_editable = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class OperationLog(Base):
    """操作日志"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String(30), nullable=False)  # operation, alarm, login
    module = Column(String(50))
    action = Column(String(50))
    description = Column(Text)
    operator_id = Column(Integer)
    operator_name = Column(String(50))
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    request_url = Column(String(500))
    request_method = Column(String(10))
    request_params = Column(Text)
    response_code = Column(Integer)
    response_time = Column(Integer)  # 响应时间(ms)
    created_at = Column(DateTime, server_default=func.now())


class Interface(Base):
    """接口配置"""
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    interface_type = Column(String(30))  # restful, soap, mqtt
    url = Column(String(500))
    method = Column(String(10))  # GET, POST, PUT, DELETE
    headers = Column(Text)  # 请求头JSON
    auth_type = Column(String(30))  # none, basic, token, oauth
    auth_config = Column(Text)  # 认证配置JSON
    request_template = Column(Text)
    response_mapping = Column(Text)  # 响应映射JSON
    timeout = Column(Integer, default=30)  # 超时时间(秒)
    retry_count = Column(Integer, default=3)  # 重试次数
    status = Column(String(20), default="active")  # active, inactive, error
    last_call_time = Column(DateTime)
    last_call_status = Column(String(20))
    permissions = Column(Text)  # 权限控制JSON
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
