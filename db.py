
"""Database helpers for Smart Inventory.
Uses Neon PostgreSQL via DATABASE_URL.
"""

import os
from contextlib import contextmanager
from datetime import timezone
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg2
import streamlit as st

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


load_dotenv()

# Pakistan Standard Time
PAKISTAN_TZ = ZoneInfo("Asia/Karachi")


def _database_url() -> str:
    try:
        value = st.secrets.get("DATABASE_URL", "")
    except Exception:
        value = ""

    value = value or os.getenv("DATABASE_URL", "")

    if not value:
        raise RuntimeError(
            "DATABASE_URL is missing. Add your Neon connection string "
            "to .env or .streamlit/secrets.toml."
        )

    return value


@contextmanager
def connection():
    conn = psycopg2.connect(
        _database_url(),
        connect_timeout=10,
        sslmode="require",
    )

    try:
        # Set timezone for this database session only.
        with conn.cursor() as cur:
            cur.execute("SET TIME ZONE 'Asia/Karachi'")

        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def query_df(sql: str, params=None) -> pd.DataFrame:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall() if cur.description else []
            columns = (
                [item[0] for item in cur.description]
                if cur.description else []
            )

    df = pd.DataFrame(rows, columns=columns)

    # Convert timestamp columns to Pakistan time.
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            if df[column].dt.tz is not None:
                df[column] = df[column].dt.tz_convert(PAKISTAN_TZ)

    return df


def query_one(sql: str, params=None):
    with connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return dict(row) if row else None


def execute(sql: str, params=None) -> int:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount


def execute_returning(sql: str, params=None):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone() if cur.description else None
            return row[0] if row else None


def authenticate(username: str, password: str):
    return query_one(
        """
        SELECT user_id, username, role
        FROM users
        WHERE username = %s
        AND password_hash = crypt(%s, password_hash)
        """,
        (username, password),
    )


def to_local(value):
    """Convert a datetime value to Pakistan Standard Time."""

    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(PAKISTAN_TZ)


def health_check() -> bool:
    query_one("SELECT 1 AS ok")
    return True
