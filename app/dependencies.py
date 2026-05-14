"""
Shared Dependencies
===================
Re-exports commonly used FastAPI dependencies so routes can import from one place.

Usage in routes:
    from app.dependencies import get_db, get_current_user, require_admin
"""

from app.core.database import get_db
from app.core.security import get_current_user, require_admin

__all__ = ["get_db", "get_current_user", "require_admin"]
