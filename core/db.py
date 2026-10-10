"""Acceso PostgreSQL con tiempos de conexión acotados."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg


@contextmanager
def connection() -> Iterator[psycopg.Connection]:
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        raise RuntimeError("DATABASE_URL no está configurada")
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        yield conn


def check_database() -> bool:
    with connection() as conn:
        return conn.execute("SELECT 1").fetchone() == (1,)
