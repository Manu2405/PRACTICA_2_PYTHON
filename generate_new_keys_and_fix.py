import os, sys
sys.path.insert(0, os.path.abspath("."))
from Crypto.PublicKey import RSA, ECC
from etl.extract import extract_csv
from etl.transform import transform_row
from etl.engine_factory import get_sqlalchemy_engine
from sqlalchemy import text
from etl.load_sqlserver import insert_sqlserver_batch
from etl.load_postgres import insert_postgres_batch
import services.crypto.keys

print("Generating new RSA Keypair for FIE...")
rsa_key = RSA.generate(2048)
new_rsa_pub = rsa_key.publickey().export_key().decode()
new_rsa_priv = rsa_key.export_key().decode()

print("Generating new ECC Keypair for Desarrollo Productivo...")
ecc_key = ECC.generate(curve="P-256")
new_ecc_pub = ecc_key.public_key().export_key(format="PEM")
new_ecc_priv = ecc_key.export_key(format="PEM")

# Temporarily mock the public keys in memory for the ETL router to use
services.crypto.keys.RSA_PUBLIC_KEY = new_rsa_pub
services.crypto.keys.ECC_PUBLIC_KEY = new_ecc_pub

print("Extracting Data...")
data = extract_csv("data/cuentas.csv")

print("Processing FIE (ID: 11)...")
fie_data = [d for d in data if int(d["IdBanco"]) == 11]
fie_transformed = [transform_row(row) for row in fie_data]
with get_sqlalchemy_engine("sqlserver", "fie").begin() as conn:
    conn.execute(text("TRUNCATE TABLE cuentas;"))
insert_sqlserver_batch("fie", fie_transformed)

print("Processing Desarrollo Productivo (ID: 13)...")
dp_data = [d for d in data if int(d["IdBanco"]) == 13]
dp_transformed = [transform_row(row) for row in dp_data]
with get_sqlalchemy_engine("postgres", "desarrollo_productivo").begin() as conn:
    conn.execute(text("TRUNCATE TABLE cuentas;"))
insert_postgres_batch("desarrollo_productivo", dp_transformed)

print("\n--- NEW RSA PRIVATE KEY (FIE) ---")
print(new_rsa_priv)
print("\n--- NEW ECC PRIVATE KEY (Desarrollo Productivo) ---")
print(new_ecc_priv)

with open("new_keys.txt", "w") as f:
    f.write(f"RSA_PUB:\n{new_rsa_pub}\n\nRSA_PRIV:\n{new_rsa_priv}\n\nECC_PUB:\n{new_ecc_pub}\n\nECC_PRIV:\n{new_ecc_priv}\n")

print("\nSaved new keys to new_keys.txt. Reloaded FIE and Desarrollo Productivo databases.")
