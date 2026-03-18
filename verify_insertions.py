import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))
from etl.config import (
    MYSQL_BASES, POSTGRES_BASES, SQLSERVER_BASES, MONGO_BASES, NEO4J_BANK,
    get_mysql_conn, get_postgres_conn, get_sqlserver_conn,
    MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
)
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from neo4j import GraphDatabase

load_dotenv(".env")

def safe_query_sql(engine, query, params=None):
    with engine.connect() as conn:
        try:
            res = conn.execute(text(query), params or {}).fetchone()
            if res:
                return dict(res._mapping)
        except Exception as e:
            pass
    return None

print("--- MySQL DBs ---")
for bank_id, db_name in MYSQL_BASES.items():
    engine = create_engine(get_mysql_conn(db_name))
    res = safe_query_sql(engine, "SELECT NroCuenta, codigo_verificacion FROM cuentas WHERE codigo_verificacion IS NOT NULL LIMIT 1")
    print(f"MySQL {db_name}: {res}")

print("\n--- Postgres DBs ---")
for bank_id, db_name in POSTGRES_BASES.items():
    engine = create_engine(get_postgres_conn(db_name))
    col = "nro_cuenta" if db_name == "desarrollo_productivo" else "nrocuenta"
    res = safe_query_sql(engine, f"SELECT {col}, codigo_verificacion FROM cuentas WHERE codigo_verificacion IS NOT NULL LIMIT 1")
    print(f"Postgres {db_name}: {res}")

print("\n--- SQL Server DBs ---")
for bank_id, db_name in SQLSERVER_BASES.items():
    engine = create_engine(get_sqlserver_conn(db_name))
    res = safe_query_sql(engine, "SELECT NroCuenta, codigo_verificacion FROM cuentas WHERE codigo_verificacion IS NOT NULL")
    print(f"SQL Server {db_name}: {res}")

print("\n--- MongoDB DBs ---")
mc = MongoClient(MONGO_URI)
for bank_id, db_name in MONGO_BASES.items():
    db = mc[db_name]
    res = db.cuentas.find_one({"codigo_verificacion": {"$ne": None}}, {"nrocuenta": 1, "codigo_verificacion": 1, "_id": 0})
    print(f"MongoDB {db_name}: {res}")

print("\n--- Neo4j DB ---")
try:
    nd = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with nd.session() as s:
        res = s.run("MATCH (c:Cuenta) WHERE c.codigo_verificacion IS NOT NULL RETURN c.NroCuenta as nro, c.codigo_verificacion as code LIMIT 1").single()
        if res:
            print(f"Neo4j: {{'nrocuenta': {res['nro']}, 'codigo_verificacion': '{res['code']}'}}")
        else:
            print("Neo4j: None")
except Exception as e:
    print(f"Neo4j: Error {e}")
