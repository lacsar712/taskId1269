from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserResponse
from app.services.auth import verify_password, create_access_token, get_current_active_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        email=current_user.email,
        phone=current_user.phone,
        department=current_user.department,
        position=current_user.position,
        role_id=current_user.role_id,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        role_name=current_user.role.name if current_user.role else None
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    return {"message": "退出成功"}
