from sqlalchemy import text
from etl.engine_factory import get_sqlalchemy_engine


def _get_postgres_column_names(db_name):
    """Get the correct column names for the Postgres database."""
    # desarrollo_productivo usa nombres con guiones (nro_cuenta, id_banco, saldo)
    if db_name == "desarrollo_productivo":
        return "nro_cuenta", "id_banco", "saldo"
    # Las otras BDs usan nombres sin guiones (nrocuenta, idbanco, saldousd)
    else:
        return "nrocuenta", "idbanco", "saldousd"


def insert_postgres(db_name, row):

    engine = get_sqlalchemy_engine("postgres", db_name)
    nro_cuenta_col, id_banco_col, saldo_col = _get_postgres_column_names(db_name)

    with engine.begin() as conn:

        conn.execute(
            text(f"""
            INSERT INTO cuentas
            (nro, identificacion, nombres, apellidos, {nro_cuenta_col}, {id_banco_col}, {saldo_col})
            VALUES (:nro, :identificacion, :nombres, :apellidos, :nrocuenta, :idbanco, :saldo)
            """),
            {
                "nro": row["Nro"],
                "identificacion": row["Identificacion"],
                "nombres": row["Nombres"],
                "apellidos": row["Apellidos"],
                "nrocuenta": row["NroCuenta"],
                "idbanco": row["IdBanco"],
                "saldo": row["Saldo"]
            }
        )


def insert_postgres_batch(db_name, rows, batch_size: int = 1000):
    """Insert multiple rows into Postgres efficiently using a single connection."""

    engine = get_sqlalchemy_engine("postgres", db_name)
    nro_cuenta_col, id_banco_col, saldo_col = _get_postgres_column_names(db_name)

    def _chunks(iterable, size):
        for i in range(0, len(iterable), size):
            yield iterable[i : i + size]

    success_count = 0
    error_count = 0

    for batch in _chunks(rows, batch_size):
        with engine.begin() as conn:
            for r in batch:
                try:
                    conn.execute(
                        text(f"""
                        INSERT INTO cuentas
                        (nro, identificacion, nombres, apellidos, {nro_cuenta_col}, {id_banco_col}, {saldo_col})
                        VALUES (:nro, :identificacion, :nombres, :apellidos, :nrocuenta, :idbanco, :saldo)
                        """),
                        {
                            "nro": r["Nro"],
                            "identificacion": r["Identificacion"],
                            "nombres": r["Nombres"],
                            "apellidos": r["Apellidos"],
                            "nrocuenta": r["NroCuenta"],
                            "idbanco": r["IdBanco"],
                            "saldo": r["Saldo"],
                        }
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Solo mostrar primeros 5 errores
                        print(f"Error en Postgres {db_name}: {str(e)[:200]}")

    if error_count > 0:
        print(f"Postgres {db_name}: {success_count} inserted, {error_count} errors")
