"""
Monitoring Route
================
A simple dashboard endpoint that returns server health and key business metrics.
Useful for quickly checking system status without opening the database manually.

GET /monitoring  →  returns JSON with counts and health status
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.product import Product, Category
from app.models.order import Order
from app.cache.redis_cache import get_redis
import platform
import datetime

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/", summary="System health and business metrics dashboard")
def monitoring_dashboard(db: Session = Depends(get_db)):
    """
    Returns a snapshot of the system's health and key statistics.

    No authentication required — useful during demos and discussions.
    """

    # ── Count business entities ───────────────────────────────────────────────
    total_users     = db.query(User).count()
    total_customers = db.query(User).filter(User.role == "customer").count()
    total_admins    = db.query(User).filter(User.role == "admin").count()
    active_users    = db.query(User).filter(User.is_active == True).count()

    total_products  = db.query(Product).count()
    out_of_stock    = db.query(Product).filter(Product.stock == 0).count()
    total_categories = db.query(Category).count()

    total_orders    = db.query(Order).count()
    pending_orders  = db.query(Order).filter(Order.status == "pending").count()
    processing      = db.query(Order).filter(Order.status == "processing").count()
    shipped         = db.query(Order).filter(Order.status == "shipped").count()
    delivered       = db.query(Order).filter(Order.status == "delivered").count()
    cancelled       = db.query(Order).filter(Order.status == "cancelled").count()

    # ── Check Redis connectivity ──────────────────────────────────────────────
    redis_client = get_redis()
    redis_status = "connected" if redis_client else "unavailable"

    return {
        "server": {
            "status":     "healthy",
            "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
            "python":     platform.python_version(),
            "platform":   platform.system(),
            "redis":      redis_status,
        },
        "users": {
            "total":     total_users,
            "active":    active_users,
            "customers": total_customers,
            "admins":    total_admins,
        },
        "products": {
            "total":        total_products,
            "out_of_stock": out_of_stock,
            "categories":   total_categories,
        },
        "orders": {
            "total":      total_orders,
            "pending":    pending_orders,
            "processing": processing,
            "shipped":    shipped,
            "delivered":  delivered,
            "cancelled":  cancelled,
        },
    }
