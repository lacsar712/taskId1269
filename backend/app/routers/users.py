from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse, RoleCreate, RoleResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth import get_password_hash, get_current_active_user

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=PaginatedResponse[UserResponse])
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.real_name.contains(keyword))
        )
    if department:
        query = query.filter(User.department == department)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=[UserResponse(
            id=u.id,
            username=u.username,
            real_name=u.real_name,
            email=u.email,
            phone=u.phone,
            department=u.department,
            position=u.position,
            role_id=u.role_id,
            is_active=u.is_active,
            last_login=u.last_login,
            created_at=u.created_at,
            role_name=u.role.name if u.role else None
        ) for u in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        email=user_data.email,
        phone=user_data.phone,
        department=user_data.department,
        position=user_data.position,
        role_id=user_data.role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        department=user.department,
        position=user.position,
        role_id=user.role_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        role_name=user.role.name if user.role else None
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        department=user.department,
        position=user.position,
        role_id=user.role_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        role_name=user.role.name if user.role else None
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        department=user.department,
        position=user.position,
        role_id=user.role_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        role_name=user.role.name if user.role else None
    )


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    db.delete(user)
    db.commit()
    return MessageResponse(message="删除成功")


# 角色管理
@router.get("/roles/list", response_model=List[RoleResponse])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    roles = db.query(Role).all()
    return roles


@router.post("/roles", response_model=RoleResponse)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db.query(Role).filter(Role.code == role_data.code).first():
        raise HTTPException(status_code=400, detail="角色编码已存在")
    
    role = Role(**role_data.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
