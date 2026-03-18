import os, sys
sys.path.insert(0, os.path.abspath("."))
from etl.extract import extract_csv
from etl.transform import transform_row
from etl.engine_factory import get_sqlalchemy_engine
from sqlalchemy import text

# Redefine encrypt for BCP
from etl.crypto_router import encrypt_by_bank

data = extract_csv("data/cuentas.csv")
bcp_data = [d for d in data if int(d["IdBanco"]) == 4]
transformed = [transform_row(row) for row in bcp_data]

engine = get_sqlalchemy_engine("mysql", "bcp")
with engine.begin() as conn:
    print("Clearing old BCP data...")
    conn.execute(text("TRUNCATE TABLE cuentas;"))
    print("Deleted old BCP records.")

# Re-insert
from etl.load_mysql import insert_mysql_batch
insert_mysql_batch("bcp", transformed)
print("Reloaded BCP accounts!")
