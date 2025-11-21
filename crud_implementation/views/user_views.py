"""
User Views (API Endpoints)
MVC Pattern: View Layer (API Interface)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.user_controller import UserController
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all users with pagination"""
    controller = UserController(db)
    users = controller.get_all_users(skip=skip, limit=limit)
    return {"users": [user.to_dict() for user in users], "count": len(users)}

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    controller = UserController(db)
    user = controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()

@router.post("/")
def create_user(
    username: str,
    email: str,
    full_name: Optional[str] = None,
    bio: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    controller = UserController(db)
    try:
        user = controller.create_user(
            username=username,
            email=email,
            full_name=full_name,
            bio=bio
        )
        return {"message": "User created successfully", "user": user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}")
def update_user(
    user_id: int,
    full_name: Optional[str] = None,
    bio: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update user information"""
    controller = UserController(db)
    
    # Prepare update data
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if bio is not None:
        update_data["bio"] = bio
    if is_active is not None:
        update_data["is_active"] = is_active
    
    user = controller.update_user(user_id, **update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User updated successfully", "user": user.to_dict()}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    controller = UserController(db)
    success = controller.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.get("/search/")
def search_users(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Search users by username, email, or full name"""
    controller = UserController(db)
    users = controller.search_users(query)
    return {"users": [user.to_dict() for user in users], "count": len(users)}

@router.post("/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db)):
    """Activate user account"""
    controller = UserController(db)
    success = controller.activate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User activated successfully"}

@router.post("/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Deactivate user account"""
    controller = UserController(db)
    success = controller.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated successfully"}

