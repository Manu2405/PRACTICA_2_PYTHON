from sqlalchemy import text
from etl.engine_factory import get_sqlalchemy_engine


def insert_mysql(db_name, row):

    engine = get_sqlalchemy_engine("mysql", db_name)

    with engine.begin() as conn:

        conn.execute(
            text("""
            INSERT INTO cuentas
            (Nro, Identificacion, Nombres, Apellidos, NroCuenta, IdBanco, SaldoUSD)
            VALUES (:nro, :identificacion, :nombres, :apellidos, :nro_cuenta, :id_banco, :saldo)
            """),
            {
                "nro": row["Nro"],
                "identificacion": row["Identificacion"],
                "nombres": row["Nombres"],
                "apellidos": row["Apellidos"],
                "nro_cuenta": row["NroCuenta"],
                "id_banco": row["IdBanco"],
                "saldo": row["Saldo"]
            }
        )


def insert_mysql_batch(db_name, rows, batch_size: int = 1000):
    """Insert multiple rows into MySQL efficiently using a single connection.

    This avoids opening/closing connections per row and relies on SQLAlchemy's
    connection pooling.
    """

    engine = get_sqlalchemy_engine("mysql", db_name)

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
                        text("""
                        INSERT INTO cuentas
                        (Nro, Identificacion, Nombres, Apellidos, NroCuenta, IdBanco, SaldoUSD)
                        VALUES (:nro, :identificacion, :nombres, :apellidos, :nro_cuenta, :id_banco, :saldo)
                        """),
                        {
                            "nro": r["Nro"],
                            "identificacion": r["Identificacion"],
                            "nombres": r["Nombres"],
                            "apellidos": r["Apellidos"],
                            "nro_cuenta": r["NroCuenta"],
                            "id_banco": r["IdBanco"],
                            "saldo": r["Saldo"],
                        }
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Solo mostrar primeros 5 errores
                        print(f"Error en MySQL {db_name}: {str(e)[:200]}")

    if error_count > 0:
        print(f"MySQL {db_name}: {success_count} inserted, {error_count} errors")
