"""
User Controller
MVC Pattern: Controller Layer (Business Logic)
"""

from sqlalchemy.orm import Session
from models.user import User
from typing import List, Optional

class UserController:
    """Controller for User operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, full_name: str = None, bio: str = None) -> User:
        """Create a new user"""
        # Check if user already exists
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        if self.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            bio=bio
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update only provided fields
        for field, value in kwargs.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def search_users(self, query: str) -> List[User]:
        """Search users by username, email, or full name"""
        return self.db.query(User).filter(
            (User.username.contains(query)) |
            (User.email.contains(query)) |
            (User.full_name.contains(query))
        ).all()
    
    def activate_user(self, user_id: int) -> bool:
        """Activate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True

