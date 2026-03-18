import re

with open("api/db.py", "r") as f:
    text = f.read()

new_code = """
from sqlalchemy import text
from etl.config import get_db_info, get_mysql_conn, get_postgres_conn, get_sqlserver_conn, MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from sqlalchemy import create_engine
from pymongo import MongoClient
from neo4j import GraphDatabase

def store_db_verification(bank_id: str, account_key: str, verification_code: str) -> None:
    engine_type, db_name = get_db_info(int(bank_id))
    
    if engine_type == "mysql":
        engine = create_engine(get_mysql_conn(db_name))
        with engine.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = :code WHERE NroCuenta = :nro"), {"code": verification_code, "nro": account_key})
    elif engine_type == "postgres":
        engine = create_engine(get_postgres_conn(db_name))
        with engine.begin() as conn:
            # Postgres could use either nrocuenta or nro_cuenta
            column_name = "nro_cuenta" if db_name == "desarrollo_productivo" else "nrocuenta"
            conn.execute(text(f"UPDATE cuentas SET codigo_verificacion = :code WHERE {column_name} = :nro"), {"code": verification_code, "nro": account_key})
    elif engine_type == "sqlserver":
        engine = create_engine(get_sqlserver_conn(db_name))
        with engine.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = :code WHERE NroCuenta = :nro"), {"code": verification_code, "nro": account_key})
    elif engine_type == "mongo":
        client = MongoClient(MONGO_URI)
        db = client[db_name]
        db.cuentas.update_one({"nrocuenta": account_key}, {"$set": {"codigo_verificacion": verification_code}})
    elif engine_type == "neo4j":
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            session.run("MATCH (c:Cuenta {NroCuenta: $nro}) SET c.codigo_verificacion = $code", {"nro": account_key, "code": verification_code})

def store_verification(bank_id: str, account_key: str, verification_code: str) -> None:
    verifs = load_verifications(bank_id)
    verifs[account_key] = {
        "verification_code": verification_code,
        "confirmed_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    save_verifications(bank_id, verifs)
    # Update DB directly as well
    try:
        from asfi.config import BANK_NAME_TO_ID
        numeric_id = str(BANK_NAME_TO_ID.get(bank_id, bank_id))
        store_db_verification(numeric_id, account_key, verification_code)
    except Exception as e:
        print(f"Error saving verification to DB for {bank_id}: {e}")
"""

text = re.sub(
    r'def store_verification\(.*?\) -> None:[\s\S]*?save_verifications\(bank_id, verifs\)',
    new_code.strip(),
    text
)

with open("api/db.py", "w") as f:
    f.write(text)

