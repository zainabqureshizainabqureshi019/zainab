
"""Secure User Management APIs for Smart Inventory."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

from backend.database import get_connection
from backend.auth import require_roles


router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

AdminOnly = Depends(require_roles("admin"))


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    role: Literal["admin", "manager", "cashier"]


class UserUpdate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    role: Literal["admin", "manager", "cashier"]


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=12)


@router.get("/")
def get_users(current_user: dict = AdminOnly):
    """Get all users. Admin only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT user_id, username, role, created_at
                FROM users
                ORDER BY user_id DESC
            """)

            return [dict(row) for row in cursor.fetchall()]


@router.get("/{user_id}")
def get_user_by_id(
    user_id: int,
    current_user: dict = AdminOnly
):
    """Get one user. Admin only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT user_id, username, role, created_at
                FROM users
                WHERE user_id = %s
            """, (user_id,))

            user = cursor.fetchone()

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            return dict(user)


@router.post("/", status_code=201)
def create_user(
    data: UserCreate,
    current_user: dict = AdminOnly
):
    """Create a user. Admin only."""

    password_hash = pwd_context.hash(data.password)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT user_id
                FROM users
                WHERE username = %s
            """, (data.username,))

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Username already exists"
                )

            cursor.execute("""
                INSERT INTO users
                    (username, password_hash, role, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING user_id, username, role, created_at
            """, (
                data.username,
                password_hash,
                data.role
            ))

            new_user = dict(cursor.fetchone())

        conn.commit()

    return {
        "message": "User created successfully",
        "user": new_user
    }


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: dict = AdminOnly
):
    """Update username and role. Admin only."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT user_id
                FROM users
                WHERE username = %s
                AND user_id != %s
            """, (data.username, user_id))

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Username already exists"
                )

            cursor.execute("""
                UPDATE users
                SET username = %s,
                    role = %s
                WHERE user_id = %s
                RETURNING user_id, username, role, created_at
            """, (
                data.username,
                data.role,
                user_id
            ))

            updated_user = cursor.fetchone()

            if updated_user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

        conn.commit()

    return {
        "message": "User updated successfully",
        "user": dict(updated_user)
    }


@router.post("/change-password")
def change_password(
    data: PasswordChange,
    current_user: dict = AdminOnly
):
    """Allow admin to securely change their own password."""

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT password_hash
                FROM users
                WHERE user_id = %s
            """, (current_user["user_id"],))

            user = cursor.fetchone()

            if user is None or not pwd_context.verify(
                data.current_password,
                user["password_hash"]
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Current password is incorrect"
                )

            new_hash = pwd_context.hash(data.new_password)

            cursor.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
            """, (new_hash, current_user["user_id"]))

        conn.commit()

    return {"message": "Password changed successfully"}
