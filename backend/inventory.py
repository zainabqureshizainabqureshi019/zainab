
"""Inventory APIs for Smart Inventory."""

import psycopg2

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from backend.database import get_connection
from backend.auth import require_roles


router = APIRouter(prefix="/inventory", tags=["Inventory"])


# Admin and Manager permissions
ManagerOrAdmin = Depends(require_roles("admin", "manager"))


class InventoryCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


@router.get("/")
def get_inventory(current_user: dict = ManagerOrAdmin):
    """Get all inventory records. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    i.inventory_id,
                    i.product_id,
                    p.name AS product_name,
                    i.quantity,
                    i.updated_at
                FROM inventory i
                JOIN products p
                    ON i.product_id = p.product_id
                ORDER BY i.inventory_id
            """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{inventory_id}")
def get_inventory_by_id(
    inventory_id: int,
    current_user: dict = ManagerOrAdmin
):
    """Get one inventory record. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    i.inventory_id,
                    i.product_id,
                    p.name AS product_name,
                    i.quantity,
                    i.updated_at
                FROM inventory i
                JOIN products p
                    ON i.product_id = p.product_id
                WHERE i.inventory_id = %s
            """, (inventory_id,))

            record = cursor.fetchone()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    return dict(record)


@router.post("/", status_code=201)
def create_inventory(
    data: InventoryCreate,
    current_user: dict = ManagerOrAdmin
):
    """Create an inventory record. Admin and Manager only."""

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO inventory (product_id, quantity)
                    VALUES (%s, %s)
                    RETURNING *
                """, (data.product_id, data.quantity))

                new_record = dict(cursor.fetchone())

            conn.commit()

        return {
            "message": "Inventory created successfully",
            "inventory": new_record
        }

    except psycopg2.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Product does not exist or inventory already exists"
        )


@router.put("/{inventory_id}")
def update_inventory(
    inventory_id: int,
    data: InventoryUpdate,
    current_user: dict = ManagerOrAdmin
):
    """Update inventory quantity. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                UPDATE inventory
                SET quantity = %s,
                    updated_at = NOW()
                WHERE inventory_id = %s
                RETURNING *
            """, (data.quantity, inventory_id))

            updated_record = cursor.fetchone()

        conn.commit()

    if updated_record is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    return {
        "message": "Inventory updated successfully",
        "inventory": dict(updated_record)
    }
