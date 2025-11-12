from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UpdateUsernameRequest,
    UpdatePasswordRequest
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 如果要更新邮箱，检查是否已存在
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    # 如果要更新用户名，检查是否已存在
    if user_update.username and user_update.username != current_user.username:
        existing_username = db.query(User).filter(User.username == user_update.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    # 如果要更新密码
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.put("/me/username", response_model=UserResponse)
async def update_username(
    request: UpdateUsernameRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的用户名"""
    # 检查用户名是否已存在
    if request.username != current_user.username:
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = request.username
        db.commit()
        db.refresh(current_user)

    return current_user


@router.put("/me/password")
async def update_password(
    request: UpdatePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的密码"""
    # 验证当前密码
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # 更新密码
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # 验证文件大小 (5MB)
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 移回文件开头

    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 5MB"
        )

    # 创建用户头像目录
    avatar_dir = Path(settings.UPLOAD_DIR) / "avatars" / str(current_user.id)
    avatar_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    file_ext = Path(file.filename).suffix if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = avatar_dir / unique_filename

    try:
        # 保存文件
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 删除旧头像（如果存在）
        if current_user.avatar_url:
            old_avatar_path = Path(current_user.avatar_url)
            if old_avatar_path.exists():
                try:
                    old_avatar_path.unlink()
                except Exception as e:
                    print(f"Failed to delete old avatar: {e}")

        # 更新用户头像 URL（相对路径）
        current_user.avatar_url = str(file_path)
        db.commit()
        db.refresh(current_user)

        return current_user

    except Exception as e:
        # 如果保存失败，删除已上传的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )
