"""Connection factory and cache for the ETL load step.

This module ensures that we reuse SQLAlchemy Engine instances across multiple
inserts (and multiple banks), avoiding the overhead of creating a new engine
per row.
"""

from sqlalchemy import create_engine

from etl.config import (
    get_mysql_conn,
    get_postgres_conn,
    get_sqlserver_conn,
)


# Cache engines for the lifetime of the process.
_ENGINES = {}


def get_sqlalchemy_engine(engine_type: str, db_name: str):
    """Return a cached SQLAlchemy engine for the given engine type and database.

    The cache key is a simple combination of the engine type and database name.
    """

    key = f"{engine_type}:{db_name}"

    if key in _ENGINES:
        return _ENGINES[key]

    if engine_type == "mysql":
        uri = get_mysql_conn(db_name)
    elif engine_type == "postgres":
        uri = get_postgres_conn(db_name)
    elif engine_type == "sqlserver":
        uri = get_sqlserver_conn(db_name)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")

    engine = create_engine(uri, pool_pre_ping=True)
    _ENGINES[key] = engine
    return engine


def dispose_all_engines():
    """Dispose all cached engines (useful for clean shutdowns/tests)."""

    for engine in _ENGINES.values():
        engine.dispose()
    _ENGINES.clear()
