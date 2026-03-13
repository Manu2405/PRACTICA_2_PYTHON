from typing import Optional

import asyncpg


_pool: Optional[asyncpg.Pool] = None


async def init_db(dsn: str) -> None:
    """
    Inicializa el pool de conexiones a PostgreSQL (db_asfi).

    Forzamos ssl=False porque tu servidor local no usa SSL.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn, ssl=False)


async def close_db() -> None:
    """
    Cierra el pool de conexiones.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """
    Devuelve el pool activo o lanza error si no se ha inicializado.
    """
    if _pool is None:
        raise RuntimeError("ASFI DB pool not initialized. Did you call init_db() on startup?")
    return _pool

