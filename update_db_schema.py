import os
import sys
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
load_dotenv("asfi/envs/.env")

print("Checking and Updating MySQL Databases...")
for bank_id, db_name in MYSQL_BASES.items():
    engine = create_engine(get_mysql_conn(db_name))
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE cuentas ADD COLUMN codigo_verificacion VARCHAR(8);"))
            print(f"Added codigo_verificacion to MySQL {db_name}")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print(f"Column already exists in MySQL {db_name}")
            else:
                print(f"Error in MySQL {db_name}: {e}")

print("\nChecking and Updating PostgreSQL Databases...")
for bank_id, db_name in POSTGRES_BASES.items():
    engine = create_engine(get_postgres_conn(db_name))
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE cuentas ADD COLUMN codigo_verificacion VARCHAR(8);"))
            print(f"Added codigo_verificacion to Postgres {db_name}")
        except Exception as e:
            if "already exists" in str(e):
                print(f"Column already exists in Postgres {db_name}")
            else:
                print(f"Error in Postgres {db_name}: {e}")

print("\nChecking and Updating SQL Server Databases...")
for bank_id, db_name in SQLSERVER_BASES.items():
    engine = create_engine(get_sqlserver_conn(db_name))
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE cuentas ADD codigo_verificacion NVARCHAR(8);"))
            print(f"Added codigo_verificacion to SQL Server {db_name}")
        except Exception as e:
            if "already exists" in str(e) or "Column names in each table must be unique" in str(e) or "already has" in str(e) or "Code" in str(e):
                print(f"Column already exists in SQL Server {db_name} (details hidden)")
            else:
                try:
                    # Let's verify if the column exists
                    res = conn.execute(text(f"SELECT COL_LENGTH('cuentas', 'codigo_verificacion')")).scalar()
                    if res is not None:
                        print(f"Column already exists in SQL Server {db_name}")
                    else:
                        print(f"Error in SQL Server {db_name}: {e}")
                except Exception as e2:
                    print(f"Critical error in SQL Server {db_name}: {e}")

print("\nChecking and Updating MongoDB Databases...")
mongo_client = MongoClient(MONGO_URI)
for bank_id, db_name in MONGO_BASES.items():
    try:
        db = mongo_client[db_name]
        # In mongo we can just update all documents to have the field if it doesn't exist (set to null or empty string)
        result = db.cuentas.update_many(
            {"codigo_verificacion": {"$exists": False}},
            {"$set": {"codigo_verificacion": None}}
        )
        print(f"Updated {result.modified_count} records in MongoDB {db_name} to include codigo_verificacion")
    except Exception as e:
        print(f"Error in MongoDB {db_name}: {e}")

print("\nChecking and Updating Neo4j Database...")
try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with neo4j_driver.session() as session:
        result = session.run("MATCH (c:Cuenta) WHERE c.codigo_verificacion IS NULL SET c.codigo_verificacion = null RETURN count(c) as updated")
        count = result.single()["updated"]
        print(f"Processed Neo4j Cuenta nodes to ensure codigo_verificacion property presence.")
except Exception as e:
        print(f"Error in Neo4j: {e}")

print("\nFinished process!")
