
"""Sales Management APIs for Smart Inventory."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from backend.database import get_connection
from backend.auth import get_current_user


router = APIRouter(prefix="/sales", tags=["Sales"])


class SaleCreate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    payment_method: str = Field(..., min_length=1)


class SaleItemCreate(BaseModel):
    sale_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)


def check_sale_access(sale, current_user):
    """Allow Admin/Manager all sales and Cashier only own sales."""

    if (
        current_user["role"] == "cashier"
        and sale["user_id"] != current_user["user_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only access your own sales"
        )


@router.get("/")
def get_sales(current_user: dict = Depends(get_current_user)):
    """Get sales according to user role."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            if current_user["role"] == "cashier":
                cursor.execute("""
                    SELECT
                        s.sale_id,
                        s.customer_id,
                        c.name AS customer_name,
                        s.user_id,
                        s.sale_date,
                        s.payment_method,
                        s.total_amount
                    FROM sales s
                    LEFT JOIN customers c
                        ON s.customer_id = c.customer_id
                    WHERE s.user_id = %s
                    ORDER BY s.sale_id DESC
                """, (current_user["user_id"],))

            else:
                cursor.execute("""
                    SELECT
                        s.sale_id,
                        s.customer_id,
                        c.name AS customer_name,
                        s.user_id,
                        s.sale_date,
                        s.payment_method,
                        s.total_amount
                    FROM sales s
                    LEFT JOIN customers c
                        ON s.customer_id = c.customer_id
                    ORDER BY s.sale_id DESC
                """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{sale_id}")
def get_sale_by_id(
    sale_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get one sale with items, subject to role permissions."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                SELECT
                    s.sale_id,
                    s.customer_id,
                    c.name AS customer_name,
                    s.user_id,
                    s.sale_date,
                    s.payment_method,
                    s.total_amount
                FROM sales s
                LEFT JOIN customers c
                    ON s.customer_id = c.customer_id
                WHERE s.sale_id = %s
            """, (sale_id,))

            sale = cursor.fetchone()

            if sale is None:
                raise HTTPException(
                    status_code=404,
                    detail="Sale not found"
                )

            check_sale_access(sale, current_user)

            cursor.execute("""
                SELECT
                    si.sale_item_id,
                    si.sale_id,
                    si.product_id,
                    p.name AS product_name,
                    si.quantity,
                    si.unit_price,
                    si.line_total
                FROM sale_items si
                JOIN products p
                    ON si.product_id = p.product_id
                WHERE si.sale_id = %s
                ORDER BY si.sale_item_id
            """, (sale_id,))

            items = [dict(row) for row in cursor.fetchall()]

    return {
        "sale": dict(sale),
        "items": items
    }


@router.post("/", status_code=201)
def create_sale(
    data: SaleCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a sale for the authenticated user."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO sales
                    (customer_id, user_id, sale_date,
                     payment_method, total_amount)
                VALUES (%s, %s, NOW(), %s, 0)
                RETURNING *
            """, (
                data.customer_id,
                current_user["user_id"],
                data.payment_method
            ))

            new_sale = dict(cursor.fetchone())

        conn.commit()

    return {
        "message": "Sale created successfully",
        "sale": new_sale
    }


@router.post("/items", status_code=201)
def add_sale_item(
    data: SaleItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add sale item, reduce inventory and update bill."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            # Check sale exists and retrieve its owner.
            cursor.execute("""
                SELECT sale_id, user_id
                FROM sales
                WHERE sale_id = %s
            """, (data.sale_id,))

            sale = cursor.fetchone()

            if sale is None:
                raise HTTPException(
                    status_code=404,
                    detail="Sale not found"
                )

            check_sale_access(sale, current_user)

            # Lock stock record to prevent simultaneous stock changes.
            cursor.execute("""
                SELECT quantity
                FROM inventory
                WHERE product_id = %s
                FOR UPDATE
            """, (data.product_id,))

            stock = cursor.fetchone()

            if stock is None:
                raise HTTPException(
                    status_code=404,
                    detail="Inventory record not found for this product"
                )

            if stock["quantity"] < data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient stock available"
                )

            # line_total is generated automatically by the database.
            cursor.execute("""
                INSERT INTO sale_items
                    (sale_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (
                data.sale_id,
                data.product_id,
                data.quantity,
                data.unit_price
            ))

            new_item = dict(cursor.fetchone())

            # Reduce inventory stock.
            cursor.execute("""
                UPDATE inventory
                SET quantity = quantity - %s,
                    updated_at = NOW()
                WHERE product_id = %s
                RETURNING *
            """, (data.quantity, data.product_id))

            updated_inventory = dict(cursor.fetchone())

            # Recalculate sale total.
            cursor.execute("""
                UPDATE sales
                SET total_amount = (
                    SELECT COALESCE(SUM(line_total), 0)
                    FROM sale_items
                    WHERE sale_id = %s
                )
                WHERE sale_id = %s
                RETURNING total_amount
            """, (data.sale_id, data.sale_id))

            updated_total = cursor.fetchone()["total_amount"]

        conn.commit()

    return {
        "message": "Sale item added and inventory updated successfully",
        "sale_item": new_item,
        "inventory": updated_inventory,
        "total_amount": updated_total
    }
