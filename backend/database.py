
"""PostgreSQL connection helpers for Smart Inventory."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as PGConnection


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# Load local environment variables.
# Hosting environment variables take priority.
if not os.getenv("DATABASE_URL"):
    backend_env = BACKEND_DIR / ".env"
    root_env = PROJECT_ROOT / ".env"

    if backend_env.is_file():
        load_dotenv(dotenv_path=backend_env, override=False)
    elif root_env.is_file():
        load_dotenv(dotenv_path=root_env, override=False)


def get_database_url() -> str:
    """Get PostgreSQL connection URL."""

    url = os.getenv("DATABASE_URL", "").strip()

    if not url:
        raise RuntimeError(
            "DATABASE_URL is missing. Add it to backend/.env "
            "or set it in your hosting environment variables."
        )

    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.setdefault("sslmode", "require")

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )


@contextmanager
def get_connection() -> Iterator[PGConnection]:
    """Open and safely close a PostgreSQL connection."""

    conn = psycopg2.connect(
        get_database_url(),
        connect_timeout=10
    )

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_database() -> bool:
    """Check database connection using SELECT 1."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
