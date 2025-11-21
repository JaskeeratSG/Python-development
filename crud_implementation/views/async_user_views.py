"""
Async User Views
===============

FastAPI views with async support for better concurrency.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from config.async_database import get_async_db
from controllers.async_user_controller import AsyncUserController
from models.user import User

# Create router
router = APIRouter(prefix="/users", tags=["users"])

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Dependency to get async controller
async def get_user_controller(db: AsyncSession = Depends(get_async_db)) -> AsyncUserController:
    return AsyncUserController(db)

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Create a new user asynchronously"""
    try:
        user = await controller.create_user(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            bio=user_data.bio
        )
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Get user by ID asynchronously"""
    user = await controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Get all users with pagination asynchronously"""
    users = await controller.get_all_users(skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Update user asynchronously"""
    # Convert Pydantic model to dict, excluding None values
    update_data = user_data.dict(exclude_unset=True)
    
    user = await controller.update_user(user_id, **update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Delete user asynchronously"""
    success = await controller.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.get("/search/", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=1),
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Search users asynchronously"""
    users = await controller.search_users(q)
    return [UserResponse.from_orm(user) for user in users]

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Activate user asynchronously"""
    success = await controller.activate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User activated successfully"}

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Deactivate user asynchronously"""
    success = await controller.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated successfully"}

# Batch operations - these really benefit from async
@router.post("/batch/", response_model=List[UserResponse])
async def create_multiple_users(
    users_data: List[UserCreate],
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Create multiple users in a single transaction"""
    try:
        users = await controller.create_multiple_users([user.dict() for user in users_data])
        return [UserResponse.from_orm(user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/with-orders", response_model=UserResponse)
async def get_user_with_orders(
    user_id: int,
    controller: AsyncUserController = Depends(get_user_controller)
):
    """Get user with their orders (eager loading)"""
    user = await controller.get_users_with_orders(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)
