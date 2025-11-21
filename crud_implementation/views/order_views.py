"""
Order Views (API Endpoints)
MVC Pattern: View Layer (API Interface)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.order_controller import OrderController
from typing import List, Optional

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all orders with optional filtering"""
    controller = OrderController(db)
    
    if user_id:
        orders = controller.get_orders_by_user(user_id)
    elif status:
        orders = controller.get_orders_by_status(status)
    else:
        orders = controller.get_all_orders(skip=skip, limit=limit)
    
    return {"orders": [order.to_dict() for order in orders], "count": len(orders)}

@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    controller = OrderController(db)
    order = controller.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_dict()

@router.post("/")
def create_order(
    user_id: int,
    product_id: int,
    quantity: int = Query(1, ge=1),
    shipping_address: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new order"""
    controller = OrderController(db)
    try:
        order = controller.create_order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            shipping_address=shipping_address,
            notes=notes
        )
        return {"message": "Order created successfully", "order": order.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update order status"""
    controller = OrderController(db)
    try:
        success = controller.update_order_status(order_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": f"Order status updated to {status}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel an order"""
    controller = OrderController(db)
    success = controller.cancel_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order cancelled successfully"}

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete order"""
    controller = OrderController(db)
    success = controller.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

@router.get("/statistics/")
def get_order_statistics(db: Session = Depends(get_db)):
    """Get order statistics"""
    controller = OrderController(db)
    stats = controller.get_order_statistics()
    return {"statistics": stats}

