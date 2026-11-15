
"""Customer Management APIs for Smart Inventory."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from backend.database import get_connection
from backend.auth import get_current_user, require_roles


router = APIRouter(prefix="/customers", tags=["Customers"])


# Admin and Manager permissions for updates
ManagerOrAdmin = Depends(require_roles("admin", "manager"))


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    phone: str | None = None


class CustomerUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    phone: str | None = None


@router.get("/")
def get_customers(current_user: dict = Depends(get_current_user)):
    """Get all customers. All authenticated roles."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT customer_id, name, phone, created_at
                FROM customers
                ORDER BY customer_id DESC
            """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{customer_id}")
def get_customer_by_id(
    customer_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get one customer. All authenticated roles."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT customer_id, name, phone, created_at
                FROM customers
                WHERE customer_id = %s
            """, (customer_id,))

            customer = cursor.fetchone()

            if customer is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )

            return dict(customer)


@router.post("/", status_code=201)
def create_customer(
    data: CustomerCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a customer. All authenticated roles."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO customers (name, phone, created_at)
                VALUES (%s, %s, NOW())
                RETURNING customer_id, name, phone, created_at
            """, (data.name, data.phone))

            new_customer = dict(cursor.fetchone())

        conn.commit()

    return {
        "message": "Customer created successfully",
        "customer": new_customer
    }


@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    current_user: dict = ManagerOrAdmin
):
    """Update customer information. Admin and Manager only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                UPDATE customers
                SET name = %s,
                    phone = %s
                WHERE customer_id = %s
                RETURNING customer_id, name, phone, created_at
            """, (data.name, data.phone, customer_id))

            updated_customer = cursor.fetchone()

            if updated_customer is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )

        conn.commit()

    return {
        "message": "Customer updated successfully",
        "customer": dict(updated_customer)
    }
