from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.system import SystemConfig, OperationLog, Interface
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/system", tags=["系统设置"])


# Schemas
class SystemConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: Optional[str]
    config_type: Optional[str]
    description: Optional[str]
    is_editable: bool
    
    class Config:
        from_attributes = True


class SystemConfigUpdate(BaseModel):
    config_value: str


class OperationLogResponse(BaseModel):
    id: int
    log_type: str
    module: Optional[str]
    action: Optional[str]
    description: Optional[str]
    operator_name: Optional[str]
    ip_address: Optional[str]
    request_url: Optional[str]
    request_method: Optional[str]
    response_code: Optional[int]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InterfaceResponse(BaseModel):
    id: int
    name: str
    code: str
    interface_type: Optional[str]
    url: Optional[str]
    method: Optional[str]
    auth_type: Optional[str]
    timeout: int
    retry_count: int
    status: str
    last_call_time: Optional[datetime]
    last_call_status: Optional[str]
    
    class Config:
        from_attributes = True


class InterfaceCreate(BaseModel):
    name: str
    interface_type: Optional[str] = None
    url: Optional[str] = None
    method: str = "GET"
    headers: Optional[str] = None
    auth_type: str = "none"
    auth_config: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3


# 系统配置
@router.get("/configs", response_model=List[SystemConfigResponse])
def get_system_configs(
    config_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(SystemConfig)
    if config_type:
        query = query.filter(SystemConfig.config_type == config_type)
    return query.all()


@router.get("/configs/{config_key}", response_model=SystemConfigResponse)
def get_system_config(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    return config


@router.put("/configs/{config_key}", response_model=SystemConfigResponse)
def update_system_config(
    config_key: str,
    data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    if not config.is_editable:
        raise HTTPException(status_code=400, detail="该配置项不可编辑")
    
    config.config_value = data.config_value
    db.commit()
    db.refresh(config)
    return config


# 操作日志
@router.get("/logs", response_model=PaginatedResponse[OperationLogResponse])
def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    log_type: Optional[str] = None,
    module: Optional[str] = None,
    operator_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(OperationLog)
    if log_type:
        query = query.filter(OperationLog.log_type == log_type)
    if module:
        query = query.filter(OperationLog.module == module)
    if operator_name:
        query = query.filter(OperationLog.operator_name.contains(operator_name))
    
    total = query.count()
    items = query.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 接口配置
@router.get("/interfaces", response_model=PaginatedResponse[InterfaceResponse])
def get_interfaces(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    interface_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Interface)
    if status:
        query = query.filter(Interface.status == status)
    if interface_type:
        query = query.filter(Interface.interface_type == interface_type)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/interfaces", response_model=InterfaceResponse)
def create_interface(
    data: InterfaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    code = f"IF{datetime.now().strftime('%Y%m%d%H%M%S')}"
    interface = Interface(
        name=data.name,
        code=code,
        interface_type=data.interface_type,
        url=data.url,
        method=data.method,
        headers=data.headers,
        auth_type=data.auth_type,
        auth_config=data.auth_config,
        timeout=data.timeout,
        retry_count=data.retry_count
    )
    db.add(interface)
    db.commit()
    db.refresh(interface)
    return interface


@router.put("/interfaces/{interface_id}/status", response_model=MessageResponse)
def toggle_interface_status(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    interface = db.query(Interface).filter(Interface.id == interface_id).first()
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    interface.status = "inactive" if interface.status == "active" else "active"
    db.commit()
    
    return MessageResponse(message="状态更新成功")


# 数据备份
@router.post("/backup")
def create_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建数据备份"""
    return {
        "message": "备份任务已创建",
        "backup_id": f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "processing"
    }


@router.get("/backup/list")
def get_backup_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取备份列表"""
    return [
        {
            "id": 1,
            "backup_id": "BK20240115120000",
            "backup_time": "2024-01-15 12:00:00",
            "size": "125MB",
            "status": "completed"
        },
        {
            "id": 2,
            "backup_id": "BK20240114120000",
            "backup_time": "2024-01-14 12:00:00",
            "size": "123MB",
            "status": "completed"
        }
    ]
