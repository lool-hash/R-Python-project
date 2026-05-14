"""
Products Route — with Redis Caching
=====================================
Products are cached in Redis to reduce database load.
Cache is invalidated automatically after any create / update / delete.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.product import Product, Category
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.cache.redis_cache import cache_get, cache_set, cache_delete, cache_delete_pattern
from app.logging.logger import logger

router = APIRouter(prefix="/products", tags=["Products"])

# ── Cache key helpers ─────────────────────────────────────────────────────────
def _list_key(search, category_id, min_price, max_price, in_stock, skip, limit):
    return f"products:list:{search}:{category_id}:{min_price}:{max_price}:{in_stock}:{skip}:{limit}"

def _detail_key(product_id: int):
    return f"products:detail:{product_id}"


# ── GET all products (public, with search / filter / pagination) ──────────────
@router.get("/", response_model=List[ProductResponse], summary="Browse all products")
def get_products(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by product name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Show only in-stock products"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Page size"),
):
    """
    Public endpoint — no login required.
    Supports full-text search, category filter, price range, and pagination.
    Results are cached in Redis for 5 minutes.
    """
    cache_key = _list_key(search, category_id, min_price, max_price, in_stock, skip, limit)

    # Try the cache first
    cached = cache_get(cache_key)
    if cached is not None:
        logger.debug("Returning cached product list for key: %s", cache_key)
        return cached

    # Cache miss — query the database
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is True:
        query = query.filter(Product.stock > 0)

    products = query.offset(skip).limit(limit).all()

    # Serialize and cache the result
    result = [ProductResponse.model_validate(p).model_dump(mode="json") for p in products]
    cache_set(cache_key, result, ttl=300)

    return products


# ── GET single product ────────────────────────────────────────────────────────
@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Returns a single product. Result is cached for 10 minutes."""
    cache_key = _detail_key(product_id)

    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = ProductResponse.model_validate(product).model_dump(mode="json")
    cache_set(cache_key, result, ttl=600)

    return product


# ── POST create product (admin only) ──────────────────────────────────────────
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new product (admin only)")
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Only admins can add products. Stock must be >= 0 and price > 0."""
    if data.category_id:
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    # Invalidate the product list cache after any change
    cache_delete_pattern("products:list:*")
    logger.info("Admin %s created product: %s", admin.username, product.name)

    return product


# ── PUT update product (admin only) ───────────────────────────────────────────
@router.put("/{product_id}", response_model=ProductResponse, summary="Update a product (admin only)")
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.category_id is not None:
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # Invalidate both the detail cache and the list cache
    cache_delete(_detail_key(product_id))
    cache_delete_pattern("products:list:*")
    logger.info("Admin %s updated product ID %d", admin.username, product_id)

    return product


# ── DELETE product (admin only) ───────────────────────────────────────────────
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a product (admin only)")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    cache_delete(_detail_key(product_id))
    cache_delete_pattern("products:list:*")
    logger.info("Admin %s deleted product ID %d", admin.username, product_id)
