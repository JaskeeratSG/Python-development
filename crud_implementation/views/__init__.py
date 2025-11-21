"""
Views Package
MVC Pattern: View Layer
"""

from .user_views import router as user_router
from .product_views import router as product_router
from .order_views import router as order_router

__all__ = ["user_router", "product_router", "order_router"]

