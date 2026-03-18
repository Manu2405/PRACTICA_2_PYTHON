import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))
from etl.config import MONGO_BASES, NEO4J_BANK, MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from pymongo import MongoClient
from neo4j import GraphDatabase

load_dotenv(".env")

print("--- MongoDB Schema Sample ---")
mc = MongoClient(MONGO_URI)
for bank_id, db_name in MONGO_BASES.items():
    db = mc[db_name]
    res = db.cuentas.find_one({}, {"_id": 0})
    print(f"{db_name}: {list(res.keys()) if res else 'None'}")

print("\n--- Neo4j Schema Sample ---")
try:
    nd = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with nd.session() as s:
        res = s.run("MATCH (c:Cuenta) RETURN properties(c) AS props LIMIT 1").single()
        print(f"Neo4j: {list(res['props'].keys()) if res else 'None'}")
except Exception as e:
    print(f"Neo4j Error: {e}")
