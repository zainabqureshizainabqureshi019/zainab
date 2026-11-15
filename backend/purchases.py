
"""Purchase Management APIs for Smart Inventory."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from backend.database import get_connection
from backend.auth import require_roles


router = APIRouter(prefix="/purchases", tags=["Purchases"])


# Admin and Manager permissions
ManagerOrAdmin = Depends(require_roles("admin", "manager"))


class PurchaseCreate(BaseModel):
    supplier_id: int | None = Field(default=None, gt=0)
    notes: str | None = None


class PurchaseItemCreate(BaseModel):
    purchase_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)


@router.get("/")
def get_purchases(current_user: dict = ManagerOrAdmin):
    """Get all purchases. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    p.purchase_id,
                    p.supplier_id,
                    s.name AS supplier_name,
                    p.purchase_date,
                    p.notes
                FROM purchases p
                LEFT JOIN suppliers s
                    ON p.supplier_id = s.supplier_id
                ORDER BY p.purchase_id DESC
            """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{purchase_id}")
def get_purchase_by_id(
    purchase_id: int,
    current_user: dict = ManagerOrAdmin
):
    """Get one purchase with its items. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                SELECT
                    p.purchase_id,
                    p.supplier_id,
                    s.name AS supplier_name,
                    p.purchase_date,
                    p.notes
                FROM purchases p
                LEFT JOIN suppliers s
                    ON p.supplier_id = s.supplier_id
                WHERE p.purchase_id = %s
            """, (purchase_id,))

            purchase = cursor.fetchone()

            if purchase is None:
                raise HTTPException(
                    status_code=404,
                    detail="Purchase not found"
                )

            cursor.execute("""
                SELECT
                    pi.purchase_item_id,
                    pi.purchase_id,
                    pi.product_id,
                    pr.name AS product_name,
                    pi.quantity,
                    pi.unit_cost,
                    pi.line_total
                FROM purchase_items pi
                JOIN products pr
                    ON pi.product_id = pr.product_id
                WHERE pi.purchase_id = %s
                ORDER BY pi.purchase_item_id
            """, (purchase_id,))

            items = [dict(row) for row in cursor.fetchall()]

    return {
        "purchase": dict(purchase),
        "items": items
    }


@router.post("/", status_code=201)
def create_purchase(
    data: PurchaseCreate,
    current_user: dict = ManagerOrAdmin
):
    """Create a new purchase. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO purchases
                    (supplier_id, purchase_date, notes)
                VALUES (%s, NOW(), %s)
                RETURNING *
            """, (data.supplier_id, data.notes))

            new_purchase = dict(cursor.fetchone())

        conn.commit()

    return {
        "message": "Purchase created successfully",
        "purchase": new_purchase
    }


@router.post("/items", status_code=201)
def add_purchase_item(
    data: PurchaseItemCreate,
    current_user: dict = ManagerOrAdmin
):
    """Add purchase item and update inventory. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                SELECT purchase_id
                FROM purchases
                WHERE purchase_id = %s
            """, (data.purchase_id,))

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Purchase not found"
                )

            # line_total is generated automatically by Neon.
            cursor.execute("""
                INSERT INTO purchase_items
                    (purchase_id, product_id, quantity, unit_cost)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (
                data.purchase_id,
                data.product_id,
                data.quantity,
                data.unit_cost
            ))

            new_item = dict(cursor.fetchone())

            # Increase inventory quantity.
            cursor.execute("""
                INSERT INTO inventory (product_id, quantity)
                VALUES (%s, %s)
                ON CONFLICT (product_id)
                DO UPDATE SET
                    quantity = inventory.quantity + EXCLUDED.quantity,
                    updated_at = NOW()
                RETURNING *
            """, (data.product_id, data.quantity))

            updated_inventory = dict(cursor.fetchone())

        conn.commit()

    return {
        "message": "Purchase item added and inventory updated successfully",
        "purchase_item": new_item,
        "inventory": updated_inventory
    }
