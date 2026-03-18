import os
import glob
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Clear ASFI DB
load_dotenv("asfi/envs/.env")
asfi_user = os.getenv("ASFI_DB_USER", "root")
asfi_pass = os.getenv("ASFI_DB_PASSWORD", "root123")
asfi_host = os.getenv("ASFI_DB_HOST", "localhost")
asfi_port = os.getenv("ASFI_DB_PORT", "3306")
asfi_name = os.getenv("ASFI_DB_NAME", "asfi_central")

try:
    engine = create_engine(f"mysql+pymysql://{asfi_user}:{asfi_pass}@{asfi_host}:{asfi_port}/{asfi_name}")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE Cuentas"))
    print("ASFI Central database table 'Cuentas' has been truncated.")
except Exception as e:
    print(f"Failed to clear ASFI Central database: {e}")

# 2. Clear API JSON Verifications
json_files = glob.glob("api/*_verifications.json")
for file in json_files:
    try:
        os.remove(file)
        print(f"Removed JSON cache: {file}")
    except Exception as e:
        print(f"Failed to remove {file}: {e}")

# 3. Clear API database Verification Columns
sys_path = os.path.abspath(".")
import sys
sys.path.insert(0, sys_path)
from etl.config import MYSQL_BASES, POSTGRES_BASES, SQLSERVER_BASES, MONGO_BASES, NEO4J_BANK, get_mysql_conn, get_postgres_conn, get_sqlserver_conn, MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from pymongo import MongoClient
from neo4j import GraphDatabase

print("\nClearing MySQL APIs Verification column...")
for bank_id, db_name in MYSQL_BASES.items():
    try:
        eng = create_engine(get_mysql_conn(db_name))
        with eng.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = NULL"))
        print(f"Cleared MySQL {db_name}")
    except: pass
    
print("Clearing Postgres APIs Verification column...")
for bank_id, db_name in POSTGRES_BASES.items():
    try:
        eng = create_engine(get_postgres_conn(db_name))
        with eng.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = NULL"))
        print(f"Cleared Postgres {db_name}")
    except: pass

print("Clearing SQL Server APIs Verification column...")
for bank_id, db_name in SQLSERVER_BASES.items():
    try:
        eng = create_engine(get_sqlserver_conn(db_name))
        with eng.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = NULL"))
        print(f"Cleared SQL Server {db_name}")
    except: pass

print("Clearing MongoDB APIs Verification...")
mc = MongoClient(MONGO_URI)
for bank_id, db_name in MONGO_BASES.items():
    try:
        db = mc[db_name]
        db.cuentas.update_many({}, {"$set": {"codigo_verificacion": None}})
        print(f"Cleared MongoDB {db_name}")
    except: pass

print("Clearing Neo4j API Verification...")
try:
    nd = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with nd.session() as s:
        s.run("MATCH (c:Cuenta) SET c.codigo_verificacion = NULL")
    print("Cleared Neo4j")
except: pass

# 4. Clear Logs
log_files = glob.glob("asfi/*.log")
for log in log_files:
    try:
        os.remove(log)
        print(f"Removed log file: {log}")
    except Exception as e:
        print(f"Failed to remove {log}: {e}")

print("\nEnvironment Reset Complete! Ready for a fresh test.")
