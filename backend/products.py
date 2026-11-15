
"""Product CRUD APIs for Smart Inventory."""

from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.database import get_connection
from backend.auth import require_roles


router = APIRouter(prefix="/products", tags=["Products"])


# Permission rules
ManagerOrAdmin = Depends(require_roles("admin", "manager"))
AdminOnly = Depends(require_roles("admin"))


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    sku: Optional[str] = Field(default=None, max_length=60)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    cost_price: float = Field(default=0, ge=0)
    sale_price: float = Field(default=0, ge=0)
    reorder_level: int = Field(default=5, ge=0)


@router.get("/")
def get_products(current_user: dict = ManagerOrAdmin):
    """Get all products. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT *
                FROM products
                ORDER BY product_id
            """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{product_id}")
def get_product(
    product_id: int,
    current_user: dict = ManagerOrAdmin
):
    """Get one product. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM products WHERE product_id = %s",
                (product_id,)
            )

            product = cursor.fetchone()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return dict(product)


@router.post("/", status_code=201)
def create_product(
    product: ProductCreate,
    current_user: dict = ManagerOrAdmin
):
    """Add a new product. Admin and Manager only."""

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO products (
                        name, sku, category_id, supplier_id,
                        cost_price, sale_price, reorder_level
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    product.name.strip(),
                    product.sku,
                    product.category_id,
                    product.supplier_id,
                    product.cost_price,
                    product.sale_price,
                    product.reorder_level
                ))

                new_product = dict(cursor.fetchone())

            conn.commit()

        return new_product

    except psycopg2.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="SKU already exists or category/supplier ID is invalid"
        )


@router.put("/{product_id}")
def update_product(
    product_id: int,
    product: ProductCreate,
    current_user: dict = ManagerOrAdmin
):
    """Update a product. Admin and Manager only."""

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    UPDATE products
                    SET name = %s,
                        sku = %s,
                        category_id = %s,
                        supplier_id = %s,
                        cost_price = %s,
                        sale_price = %s,
                        reorder_level = %s
                    WHERE product_id = %s
                    RETURNING *
                """, (
                    product.name.strip(),
                    product.sku,
                    product.category_id,
                    product.supplier_id,
                    product.cost_price,
                    product.sale_price,
                    product.reorder_level,
                    product_id
                ))

                updated_product = cursor.fetchone()

                if updated_product is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found"
                    )

                result = dict(updated_product)

            conn.commit()

        return result

    except psycopg2.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="SKU already exists or category/supplier ID is invalid"
        )


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: dict = AdminOnly
):
    """Deactivate a product. Admin only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                UPDATE products
                SET active = FALSE
                WHERE product_id = %s AND active = TRUE
                RETURNING product_id, name, active
            """, (product_id,))

            deleted_product = cursor.fetchone()

            if deleted_product is None:
                raise HTTPException(
                    status_code=404,
                    detail="Active product not found"
                )

        conn.commit()

    return {
        "message": "Product deactivated successfully",
        "product": dict(deleted_product)
    }
