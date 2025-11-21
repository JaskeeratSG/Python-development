"""
Async User Controller
====================

This demonstrates how to implement the user controller with asyncio
for better concurrency and performance.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from models.user import User

class AsyncUserController:
    """Async user controller with asyncio support"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, username: str, email: str, full_name: str = None, bio: str = None) -> User:
        """Create a new user asynchronously"""
        # Check if user already exists
        existing_user = await self.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        existing_email = await self.get_user_by_email(email)
        if existing_email:
            raise ValueError(f"Email '{email}' already exists")
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            bio=bio
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID asynchronously"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username asynchronously"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email asynchronously"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination asynchronously"""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information asynchronously"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update only provided fields
        for field, value in kwargs.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user asynchronously"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True
    
    async def search_users(self, query: str) -> List[User]:
        """Search users by username, email, or full name asynchronously"""
        result = await self.db.execute(
            select(User).where(
                (User.username.contains(query)) |
                (User.email.contains(query)) |
                (User.full_name.contains(query))
            )
        )
        return result.scalars().all()
    
    async def activate_user(self, user_id: int) -> bool:
        """Activate user account asynchronously"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        await self.db.commit()
        return True
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account asynchronously"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        await self.db.commit()
        return True

    # Batch operations - these really benefit from async
    async def create_multiple_users(self, users_data: List[dict]) -> List[User]:
        """Create multiple users in a single transaction"""
        users = []
        for user_data in users_data:
            user = User(**user_data)
            users.append(user)
            self.db.add(user)
        
        await self.db.commit()
        
        # Refresh all users
        for user in users:
            await self.db.refresh(user)
        
        return users
    
    async def get_users_with_orders(self, user_id: int) -> Optional[User]:
        """Get user with their orders (eager loading)"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.orders))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def bulk_update_users(self, updates: List[dict]) -> int:
        """Bulk update multiple users"""
        updated_count = 0
        for update_data in updates:
            user_id = update_data.pop('id')
            result = await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            updated_count += result.rowcount
        
        await self.db.commit()
        return updated_count
