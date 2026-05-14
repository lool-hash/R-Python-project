"""
Cart Route  — Update quantity endpoint added
=============================================
Customers can add, update, remove, or clear their cart.
All cart operations require a valid JWT token.

IMPORTANT – Route registration order matters in FastAPI:
  DELETE /        (clear cart)   must come BEFORE
  DELETE /{item_id} (remove one) otherwise FastAPI tries to coerce
  an empty string as an integer and returns 422 instead of calling
  clear_cart.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.order import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import CartItemCreate, CartItemResponse, CartItemUpdate
from app.logging.logger import logger

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


# ── View current user's cart ───────────────────────────────────────────────────
@router.get("/", response_model=List[CartItemResponse], summary="View my cart")
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns all items currently in the authenticated user's cart."""
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return items


# ── Add item to cart ──────────────────────────────────────────────────────────
@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED,
             summary="Add a product to my cart")
def add_to_cart(
    data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Adds a product to the cart. If the product is already in the cart,
    the quantity is increased instead of creating a duplicate entry.
    Validates that enough stock is available before adding.
    """
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} units available in stock"
        )

    # If item is already in the cart, just update the quantity
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == data.product_id,
    ).first()

    if existing:
        new_qty = existing.quantity + data.quantity
        if product.stock < new_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot add {data.quantity} more — only {product.stock} total in stock"
            )
        existing.quantity = new_qty
        db.commit()
        db.refresh(existing)
        logger.info("User %s updated cart item %d -> qty %d", current_user.username, existing.id, new_qty)
        return existing

    item = CartItem(
        user_id=current_user.id,
        product_id=data.product_id,
        quantity=data.quantity,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info("User %s added product %d to cart (qty=%d)", current_user.username, data.product_id, data.quantity)
    return item


# ── Update quantity of a cart item ────────────────────────────────────────────
@router.put("/{item_id}", response_model=CartItemResponse, summary="Update cart item quantity")
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set the quantity of an existing cart item. Must be >= 1."""
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product and product.stock < data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} units available in stock"
        )

    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item


# ── Clear entire cart — MUST be registered BEFORE /{item_id} ─────────────────
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Clear my entire cart")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Removes all items from the authenticated user's cart."""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    logger.info("User %s cleared their cart", current_user.username)


# ── Remove a single item from cart ────────────────────────────────────────────
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove one item from my cart")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
