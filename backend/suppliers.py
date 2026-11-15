
"""Supplier APIs for Smart Inventory."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from backend.database import get_connection
from backend.auth import require_roles


router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


# Admin and Manager permissions
ManagerOrAdmin = Depends(require_roles("admin", "manager"))


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str | None = None
    address: str | None = None


class SupplierUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str | None = None
    address: str | None = None


@router.get("/")
def get_suppliers(current_user: dict = ManagerOrAdmin):
    """Get all suppliers. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT *
                FROM suppliers
                ORDER BY supplier_id
            """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{supplier_id}")
def get_supplier_by_id(
    supplier_id: int,
    current_user: dict = ManagerOrAdmin
):
    """Get one supplier. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT *
                FROM suppliers
                WHERE supplier_id = %s
            """, (supplier_id,))

            supplier = cursor.fetchone()

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return dict(supplier)


@router.post("/", status_code=201)
def create_supplier(
    data: SupplierCreate,
    current_user: dict = ManagerOrAdmin
):
    """Create a new supplier. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO suppliers (name, phone, address)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (data.name, data.phone, data.address))

            new_supplier = dict(cursor.fetchone())

        conn.commit()

    return {
        "message": "Supplier created successfully",
        "supplier": new_supplier
    }


@router.put("/{supplier_id}")
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    current_user: dict = ManagerOrAdmin
):
    """Update supplier details. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                UPDATE suppliers
                SET name = %s,
                    phone = %s,
                    address = %s
                WHERE supplier_id = %s
                RETURNING *
            """, (
                data.name,
                data.phone,
                data.address,
                supplier_id
            ))

            updated_supplier = cursor.fetchone()

        conn.commit()

    if updated_supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return {
        "message": "Supplier updated successfully",
        "supplier": dict(updated_supplier)
    }
