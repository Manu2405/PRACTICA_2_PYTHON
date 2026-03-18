from sqlalchemy import text
from etl.engine_factory import get_sqlalchemy_engine


def insert_sqlserver(db_name, row):

    engine = get_sqlalchemy_engine("sqlserver", db_name)

    try:
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
    except Exception as e:
        print(f"Error inserting in SQL Server {db_name}: {str(e)[:100]}")


def insert_sqlserver_batch(db_name, rows, batch_size: int = 1000):
    """Insert multiple rows into SQL Server efficiently using a single connection."""

    engine = get_sqlalchemy_engine("sqlserver", db_name)

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
                        print(f"Error en SQL Server {db_name}: {str(e)[:200]}")
    
    if error_count > 0:
        print(f"SQL Server {db_name}: {success_count} inserted, {error_count} errors")
