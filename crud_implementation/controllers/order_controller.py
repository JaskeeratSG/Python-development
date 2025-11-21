"""
Order Controller
MVC Pattern: Controller Layer (Business Logic)
"""

from sqlalchemy.orm import Session
from models.order import Order
from models.user import User
from models.product import Product
from typing import List, Optional

class OrderController:
    """Controller for Order operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_order(self, user_id: int, product_id: int, quantity: int = 1, 
                    shipping_address: str = None, notes: str = None) -> Order:
        """Create a new order"""
        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if product exists and is available
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        if not product.is_available:
            raise ValueError(f"Product {product.name} is not available")
        
        if product.stock_quantity < quantity:
            raise ValueError(f"Insufficient stock. Available: {product.stock_quantity}, Requested: {quantity}")
        
        # Calculate total amount
        total_amount = product.price * quantity
        
        # Create order
        order = Order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_amount=total_amount,
            shipping_address=shipping_address,
            notes=notes
        )
        
        self.db.add(order)
        
        # Update product stock
        product.stock_quantity -= quantity
        if product.stock_quantity == 0:
            product.is_available = False
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_orders_by_user(self, user_id: int) -> List[Order]:
        """Get all orders for a specific user"""
        return self.db.query(Order).filter(Order.user_id == user_id).all()
    
    def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders with pagination"""
        return self.db.query(Order).offset(skip).limit(limit).all()
    
    def get_orders_by_status(self, status: str) -> List[Order]:
        """Get orders by status"""
        return self.db.query(Order).filter(Order.status == status).all()
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        order.status = status
        self.db.commit()
        return True
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order and restore stock"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        if order.status == "cancelled":
            return True  # Already cancelled
        
        # Restore stock
        product = self.db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.stock_quantity += order.quantity
            product.is_available = True
        
        order.status = "cancelled"
        self.db.commit()
        return True
    
    def delete_order(self, order_id: int) -> bool:
        """Delete order"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        self.db.delete(order)
        self.db.commit()
        return True
    
    def get_order_statistics(self) -> dict:
        """Get order statistics"""
        total_orders = self.db.query(Order).count()
        pending_orders = self.db.query(Order).filter(Order.status == "pending").count()
        confirmed_orders = self.db.query(Order).filter(Order.status == "confirmed").count()
        shipped_orders = self.db.query(Order).filter(Order.status == "shipped").count()
        delivered_orders = self.db.query(Order).filter(Order.status == "delivered").count()
        cancelled_orders = self.db.query(Order).filter(Order.status == "cancelled").count()
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders
        }

