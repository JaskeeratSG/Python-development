"""
Product Controller
MVC Pattern: Controller Layer (Business Logic)
"""

from sqlalchemy.orm import Session
from models.product import Product
from typing import List, Optional

class ProductController:
    """Controller for Product operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, name: str, price: float, description: str = None, 
                      category: str = None, stock_quantity: int = 0) -> Product:
        """Create a new product"""
        product = Product(
            name=name,
            price=price,
            description=description,
            category=category,
            stock_quantity=stock_quantity
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        return self.db.query(Product).offset(skip).limit(limit).all()
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        return self.db.query(Product).filter(Product.category == category).all()
    
    def get_available_products(self) -> List[Product]:
        """Get only available products"""
        return self.db.query(Product).filter(Product.is_available == True).all()
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """Update product information"""
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Update only provided fields
        for field, value in kwargs.items():
            if hasattr(product, field) and value is not None:
                setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        return True
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name or description"""
        return self.db.query(Product).filter(
            (Product.name.contains(query)) |
            (Product.description.contains(query))
        ).all()
    
    def update_stock(self, product_id: int, quantity: int) -> bool:
        """Update product stock quantity"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        product.stock_quantity = quantity
        product.is_available = quantity > 0
        self.db.commit()
        return True
    
    def toggle_availability(self, product_id: int) -> bool:
        """Toggle product availability"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        product.is_available = not product.is_available
        self.db.commit()
        return True

