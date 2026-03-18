from dotenv import load_dotenv
import os

load_dotenv()

# ======================================
# MYSQL BASES
# ======================================

MYSQL_BASES = {
    1: "banco_union",
    4: "bcp",
    10: "fortaleza"
}

# ======================================
# POSTGRES BASES
# ======================================

POSTGRES_BASES = {
    2: "mercantil",
    5: "bisa",
    9: "solidario",
    13: "desarrollo_productivo"
}

# ======================================
# SQL SERVER BASES
# ======================================

SQLSERVER_BASES = {
    3: "bnb",
    7: "economico",
    11: "fie"
}

# ======================================
# MONGODB BASES
# ======================================

MONGO_BASES = {
    6: "ganadero",
    8: "prodem",
    12: "pyme_comunidad"
}

# ======================================
# NEO4J
# ======================================

NEO4J_BANK = 14


# ======================================
# MYSQL CONNECTION BUILDER
# ======================================

def get_mysql_conn(db):

    return (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:"
        f"{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:"
        f"{os.getenv('MYSQL_PORT')}/"
        f"{db}"
    )


# ======================================
# POSTGRES CONNECTION BUILDER
# ======================================

def get_postgres_conn(db):

    return (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{db}"
    )


# ======================================
# SQL SERVER CONNECTION BUILDER
# ======================================

def get_sqlserver_conn(db):

    return (
        f"mssql+pyodbc://{os.getenv('SQLSERVER_USER')}:"
        f"{os.getenv('SQLSERVER_PASSWORD')}@"
        f"{os.getenv('SQLSERVER_HOST')}:"
        f"{os.getenv('SQLSERVER_PORT')}/"
        f"{db}"
        "?driver=FreeTDS"
    )


# ======================================
# MONGO CONNECTION
# ======================================

MONGO_URI = os.getenv("MONGO_URI")


# ======================================
# NEO4J CONNECTION
# ======================================

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


# ======================================
# ROUTER: BANCO → MOTOR + BASE
# ======================================

def get_db_info(bank_id):

    if bank_id in MYSQL_BASES:
        return "mysql", MYSQL_BASES[bank_id]

    if bank_id in POSTGRES_BASES:
        return "postgres", POSTGRES_BASES[bank_id]

    if bank_id in SQLSERVER_BASES:
        return "sqlserver", SQLSERVER_BASES[bank_id]

    if bank_id in MONGO_BASES:
        return "mongo", MONGO_BASES[bank_id]

    if bank_id == NEO4J_BANK:
        return "neo4j", "neo4j"

    return None, None