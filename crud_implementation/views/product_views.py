"""
Product Views (API Endpoints)
MVC Pattern: View Layer (API Interface)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.product_controller import ProductController
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    available_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    controller = ProductController(db)
    
    if available_only:
        products = controller.get_available_products()
    elif category:
        products = controller.get_products_by_category(category)
    else:
        products = controller.get_all_products(skip=skip, limit=limit)
    
    return {"products": [product.to_dict() for product in products], "count": len(products)}

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    controller = ProductController(db)
    product = controller.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_dict()

@router.post("/")
def create_product(
    name: str,
    price: float,
    description: Optional[str] = None,
    category: Optional[str] = None,
    stock_quantity: int = 0,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    controller = ProductController(db)
    product = controller.create_product(
        name=name,
        price=price,
        description=description,
        category=category,
        stock_quantity=stock_quantity
    )
    return {"message": "Product created successfully", "product": product.to_dict()}

@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    stock_quantity: Optional[int] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update product information"""
    controller = ProductController(db)
    
    # Prepare update data
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if price is not None:
        update_data["price"] = price
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
    if stock_quantity is not None:
        update_data["stock_quantity"] = stock_quantity
    if is_available is not None:
        update_data["is_available"] = is_available
    
    product = controller.update_product(product_id, **update_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product updated successfully", "product": product.to_dict()}

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete product"""
    controller = ProductController(db)
    success = controller.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.get("/search/")
def search_products(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Search products by name or description"""
    controller = ProductController(db)
    products = controller.search_products(query)
    return {"products": [product.to_dict() for product in products], "count": len(products)}

@router.put("/{product_id}/stock")
def update_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    """Update product stock quantity"""
    controller = ProductController(db)
    success = controller.update_stock(product_id, quantity)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Stock updated to {quantity} units"}

@router.post("/{product_id}/toggle-availability")
def toggle_availability(product_id: int, db: Session = Depends(get_db)):
    """Toggle product availability"""
    controller = ProductController(db)
    success = controller.toggle_availability(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product availability toggled successfully"}

