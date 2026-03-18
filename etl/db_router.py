from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from etl.config import get_db_info
from etl.load_mysql import insert_mysql, insert_mysql_batch
from etl.load_postgres import insert_postgres, insert_postgres_batch
from etl.load_sqlserver import insert_sqlserver, insert_sqlserver_batch
from etl.load_mongo import insert_mongo, insert_mongo_batch
from etl.load_neo4j import insert_neo4j, insert_neo4j_batch
from tqdm import tqdm


def route_insert(row):
    """Route a single row to its target database."""

    bank_id = int(row["IdBanco"])
    engine, db_name = get_db_info(bank_id)

    if engine == "mysql":
        insert_mysql(db_name, row)

    elif engine == "postgres":
        insert_postgres(db_name, row)

    elif engine == "sqlserver":
        insert_sqlserver(db_name, row)

    elif engine == "mongo":
        insert_mongo(db_name, row)

    elif engine == "neo4j":
        insert_neo4j(row)

    else:
        print("Banco no reconocido:", bank_id)


def route_insert_many(rows):
    """Route many rows in bulk to reduce connection churn.

    Groups rows by (engine, database) and uses batch insert helpers when
    available. Executes inserts in parallel for better performance.
    """

    grouped = defaultdict(list)
    for row in rows:
        bank_id = int(row["IdBanco"])
        engine, db_name = get_db_info(bank_id)
        grouped[(engine, db_name)].append(row)

    def insert_batch(engine, db_name, group):
        if engine == "mysql":
            insert_mysql_batch(db_name, group)
        elif engine == "postgres":
            insert_postgres_batch(db_name, group)
        elif engine == "sqlserver":
            insert_sqlserver_batch(db_name, group)
        elif engine == "mongo":
            insert_mongo_batch(db_name, group)
        elif engine == "neo4j":
            insert_neo4j_batch(group)
        else:
            print("Banco no reconocido:", db_name, "(engine=", engine, ")")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(insert_batch, engine, db_name, group) for (engine, db_name), group in grouped.items()]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Cargando datos en bases de datos"):
            future.result()  # Raise any exceptions that occurred
