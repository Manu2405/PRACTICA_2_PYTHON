import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
import couchdb
from datetime import datetime
import urllib.parse # Para manejar caracteres especiales en contraseñas

# ==========================================
# 1. CONFIGURACIÓN DE TUS CREDENCIALES
# ==========================================
USER = "tu_usuario"
PASS = urllib.parse.quote_plus("tu_contraseña") # Protege caracteres como @ o /
HOST = "localhost"
CSV_FILE = 'PRACTICA_2_PYTHON.csv'
AUTOR = "berriosanderson"

# ==========================================
# 2. MOTORES DE BASE DE DATOS
# ==========================================
# SQL - Creamos los enlaces
engines = {
    "postgres": create_engine(f'postgresql://{USER}:{PASS}@{HOST}:5432/postgres'),
    "mysql": create_engine(f'mysql+mysqlconnector://{USER}:{PASS}@{HOST}:3306/mysql'),
    "sqlserver": create_engine(f'mssql+pyodbc://{USER}:{PASS}@{HOST}/master?driver=SQL+Server')
}

# NoSQL - Creamos las conexiones
mongo_client = MongoClient(f'mongodb://{HOST}:27017/')
# Para CouchDB, a veces el puerto es 5984
couch_server = couchdb.Server(f'http://{USER}:{PASS}@{HOST}:5984/')

# ==========================================
# 3. DICCIONARIO DE BANCOS (IDs 1 al 14)
# ==========================================
BANCOS_MASTER = {
    1: "Banco Unión S.A.", 2: "Banco Mercantil Santa Cruz S.A.",
    3: "Banco Nacional de Bolivia S.A. (BNB)", 4: "Banco de Crédito de Bolivia S.A. (BCP)",
    5: "Banco BISA S.A.", 6: "Banco Ganadero S.A.", 7: "Banco Económico S.A.",
    8: "Banco Prodem S.A.", 9: "Banco Solidario S.A.", 10: "Banco Fortaleza S.A.",
    11: "Banco FIE S.A.", 12: "Banco PYME de la Comunidad S.A.",
    13: "Banco de Desarrollo Productivo S.A.M.", 14: "Banco de la Nación Argentina"
}

def iniciar_proceso():
    fecha_proc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 Iniciando proceso para {AUTOR}...")

    # --- A. CREAR BASE MAESTRA (TABLA 15) ---
    df_maestro = pd.DataFrame([
        {"IdBanco": k, "NombreBanco": v, "CuentaCreada": fecha_proc, "CuentaCreadaPor": AUTOR}
        for k, v in BANCOS_MASTER.items()
    ])
    
    # Guardar maestra en SQL
    for name, eng in engines.items():
        df_maestro.to_sql('tabla_maestra_bancos', eng, if_exists='replace', index=False)
    
    # Guardar maestra en NoSQL
    mongo_client["DB_MAESTRA"]["ListaBancos"].insert_many(df_maestro.to_dict('records'))
    if "db_maestra" in couch_server: del couch_server["db_maestra"]
    couch_server.create("db_maestra").update(df_maestro.to_dict('records'))

    # --- B. PROCESAR CSV POR TROZOS ---
    try:
        # Leemos de 5000 en 5000 para no explotar la RAM
        for chunk in pd.read_csv(CSV_FILE, chunksize=5000):
            chunk['CuentaCreada'] = fecha_proc
            chunk['CuentaCreadaPor'] = AUTOR

            for id_b in BANCOS_MASTER.keys():
                # Filtramos los datos que pertenecen a este banco en este trozo
                datos_banco = chunk[chunk['IdBanco'] == id_b]
                
                if not datos_banco.empty:
                    nombre_db = f"banco_{id_b}"
                    
                    # 1. Enviar a SQLs
                    for name, eng in engines.items():
                        datos_banco.to_sql(f'cuentas_{nombre_db}', eng, if_exists='append', index=False)
                    
                    # 2. Enviar a MongoDB
                    mongo_client[nombre_db]["cuentas"].insert_many(datos_banco.to_dict('records'))
                    
                    # 3. Enviar a CouchDB
                    if nombre_db not in couch_server: couch_server.create(nombre_db)
                    couch_server[nombre_db].update(datos_banco.to_dict('records'))
            
            print(f"✔ Lote de 5000 registros procesado.")

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")

if __name__ == "__main__":
    iniciar_proceso()
    print("✨ Proceso terminado. Datos repartidos en 5 motores de BD.")