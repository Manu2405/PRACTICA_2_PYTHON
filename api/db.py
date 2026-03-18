import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from etl.config import get_db_info, MONGO_URI, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from etl.engine_factory import get_sqlalchemy_engine
from neo4j import GraphDatabase
from pymongo import MongoClient
from sqlalchemy import text


# Local copy of bank mappings (since we can't modify etl/config.py)
MYSQL_BASES = {1: "banco_union", 4: "bcp", 10: "fortaleza"}
POSTGRES_BASES = {2: "mercantil", 5: "bisa", 9: "solidario", 13: "desarrollo_productivo"}
SQLSERVER_BASES = {3: "bnb", 7: "economico", 11: "fie"}
MONGO_BASES = {6: "ganadero", 8: "prodem", 12: "pyme_comunidad"}
NEO4J_BANK = 14

BANK_NAME_TO_ID = {
    **{v: k for k, v in MYSQL_BASES.items()},
    **{v: k for k, v in POSTGRES_BASES.items()},
    **{v: k for k, v in SQLSERVER_BASES.items()},
    **{v: k for k, v in MONGO_BASES.items()},
    "argentina": NEO4J_BANK,
}


def get_bank_id(bank):
    """Resolve a bank identifier (name or numeric) into its numeric ID."""
    if isinstance(bank, int):
        return bank
    if isinstance(bank, str) and bank.isdigit():
        return int(bank)
    return BANK_NAME_TO_ID.get(bank)


def local_get_db_info(bank_id):
    """Local copy of get_db_info that handles string bank names."""
    bank_id = get_bank_id(bank_id)

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


def _ensure_verifications_dir() -> Path:
    path = Path(__file__).parent / "verifications"
    path.mkdir(exist_ok=True)
    return path


def _verification_path(bank_id: str) -> Path:
    return _ensure_verifications_dir() / f"{bank_id}.json"


def load_verifications(bank_id: str) -> Dict[str, Any]:
    path = _verification_path(bank_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_verifications(bank_id: str, payload: Dict[str, Any]) -> None:
    path = _verification_path(bank_id)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


from sqlalchemy import text
from etl.config import get_db_info, get_mysql_conn, get_postgres_conn, get_sqlserver_conn, MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from sqlalchemy import create_engine
from pymongo import MongoClient
from neo4j import GraphDatabase

_engine_cache = {}

def get_cached_engine(engine_type, db_name):
    cache_key = f"{engine_type}_{db_name}"
    if cache_key not in _engine_cache:
        if engine_type == "mysql":
            _engine_cache[cache_key] = create_engine(get_mysql_conn(db_name), pool_size=10, max_overflow=20)
        elif engine_type == "postgres":
            _engine_cache[cache_key] = create_engine(get_postgres_conn(db_name), pool_size=10, max_overflow=20)
        elif engine_type == "sqlserver":
            _engine_cache[cache_key] = create_engine(get_sqlserver_conn(db_name), pool_size=10, max_overflow=20)
    return _engine_cache.get(cache_key)

_mongo_client = None
def get_cached_mongo():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI, maxPoolSize=20)
    return _mongo_client

_neo4j_driver = None
def get_cached_neo4j():
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), max_connection_pool_size=20)
    return _neo4j_driver

def store_db_verification(bank_id: str, account_key: str, verification_code: str) -> None:
    engine_type, db_name = get_db_info(int(bank_id))
    
    if engine_type == "mysql":
        engine = get_cached_engine(engine_type, db_name)
        with engine.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = :code WHERE NroCuenta = :nro"), {"code": verification_code, "nro": account_key})
    elif engine_type == "postgres":
        engine = get_cached_engine(engine_type, db_name)
        with engine.begin() as conn:
            # Postgres could use either nrocuenta or nro_cuenta
            column_name = "nro_cuenta" if db_name == "desarrollo_productivo" else "nrocuenta"
            conn.execute(text(f"UPDATE cuentas SET codigo_verificacion = :code WHERE {column_name} = :nro"), {"code": verification_code, "nro": account_key})
    elif engine_type == "sqlserver":
        engine = get_cached_engine(engine_type, db_name)
        with engine.begin() as conn:
            conn.execute(text("UPDATE cuentas SET codigo_verificacion = :code WHERE NroCuenta = :nro"), {"code": verification_code, "nro": account_key})
    elif engine_type == "mongo":
        client = get_cached_mongo()
        db = client[db_name]
        try:
            account_nro = int(account_key)
        except ValueError:
            account_nro = account_key
        db.cuentas.update_one({"NroCuenta": account_nro}, {"$set": {"codigo_verificacion": verification_code}})
    elif engine_type == "neo4j":
        driver = get_cached_neo4j()
        with driver.session() as session:
            try:
                account_nro = int(account_key)
            except ValueError:
                account_nro = account_key
            session.run("MATCH (c:Cuenta {numero: $nro}) SET c.codigo_verificacion = $code", {"nro": account_nro, "code": verification_code})

def store_verification(bank_id: str, account_key: str, verification_code: str) -> None:
    verifs = load_verifications(bank_id)
    verifs[account_key] = {
        "verification_code": verification_code,
        "confirmed_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    save_verifications(bank_id, verifs)
    # Update DB directly as well
    try:
        bank_map = {
            "banco_union": 1, "mercantil": 2, "bnb": 3, "bcp": 4, 
            "bisa": 5, "ganadero": 6, "economico": 7, "prodem": 8, 
            "solidario": 9, "fortaleza": 10, "fie": 11, 
            "pyme_comunidad": 12, "desarrollo_productivo": 13, "argentina": 14
        }
        numeric_id = str(bank_map.get(bank_id, bank_id))
        store_db_verification(numeric_id, account_key, verification_code)
    except Exception as e:
        import traceback
        with open("db_errors.log", "a") as ef:
            ef.write(f"Error saving verification to DB for {bank_id}: {e}\n{traceback.format_exc()}\n==========\n")
        print(f"Error saving verification to DB for {bank_id}: {e}")


def list_verifications(bank_id: str) -> Dict[str, Any]:
    return load_verifications(bank_id)


def _normalize_account_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize account dictionary keys to CamelCase regardless of source format."""
    
    # Create a lowercase version for lookup
    lower_row = {k.lower(): v for k, v in row.items()}
    
    return {
        "Nro": lower_row.get("nro"),
        "Identificacion": lower_row.get("identificacion"),
        "Nombres": lower_row.get("nombres"),
        "Apellidos": lower_row.get("apellidos"),
        "NroCuenta": lower_row.get("nrocuenta") or lower_row.get("nro_cuenta"),
        "IdBanco": lower_row.get("idbanco") or lower_row.get("bancoid") or lower_row.get("id_banco"),
        "Saldo": lower_row.get("saldo"),
        "SaldoUSD": lower_row.get("saldousd"),
        "SaldoBs": lower_row.get("saldobs"),
    }


def _fetch_sql_rows(engine_type: str, db_name: str, limit: int, offset: int) -> List[Dict[str, Any]]:
    engine = get_sqlalchemy_engine(engine_type, db_name)
    with engine.connect() as conn:
        if engine_type == "sqlserver":
            # SQL Server requires ORDER BY for OFFSET/FETCH, and uses different syntax
            query = text("SELECT * FROM cuentas ORDER BY (SELECT NULL) OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY")
        else:
            query = text("SELECT * FROM cuentas LIMIT :limit OFFSET :offset")
        result = conn.execute(query, {"limit": limit, "offset": offset})
        rows = [_normalize_account_dict(dict(row)) for row in result.mappings().all()]
        return rows


def _fetch_mongo_rows(db_name: str, limit: int, offset: int) -> List[Dict[str, Any]]:
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    cursor = db["cuentas"].find({}).skip(offset).limit(limit)
    rows = []
    for doc in cursor:
        normalized = _normalize_account_dict(doc)
        # Handle ObjectId serialization
        if "_id" in doc:
            normalized["_id"] = str(doc["_id"])
        rows.append(normalized)
    return rows


def _fetch_neo4j_rows(limit: int, offset: int) -> List[Dict[str, Any]]:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run(
            """
            MATCH (cl:Cliente)-[:TIENE]->(c:Cuenta)
            RETURN 
                c.nro AS Nro, 
                cl.ci AS Identificacion,
                cl.nombre AS Nombres,
                cl.apellido AS Apellidos,
                c.numero AS NroCuenta,
                c.banco AS IdBanco,
                c.saldo AS SaldoUSD
            ORDER BY c.nro
            SKIP $offset 
            LIMIT $limit
            """,
            limit=limit,
            offset=offset,
        )
        return [dict(record) for record in result]


def fetch_accounts(
    bank_id: str,
    limit: int = 100,
    offset: int = 0,
    parallel: bool = False,
    workers: int = 4,
) -> List[Dict[str, Any]]:
    """Fetch account rows from the bank's database.

    If `parallel=True`, the function will perform multiple reads in parallel to
    improve throughput when retrieving large volumes.
    """

    numeric_bank_id = get_bank_id(bank_id)
    engine_type, db_name = local_get_db_info(numeric_bank_id)

    if engine_type is None:
        return []

    if not parallel or limit <= 0 or workers <= 1:
        return _fetch_accounts(engine_type, db_name, limit, offset)

    # Split the range into chunks and fetch in parallel.
    chunk_size = max(1, limit // workers)
    offsets = [offset + i * chunk_size for i in range(workers)]
    limits = [chunk_size] * workers

    # Ensure we cover the full limit (last chunk may be larger)
    remaining = limit - chunk_size * workers
    if remaining > 0:
        limits[-1] += remaining

    results: List[Dict[str, Any]] = []

    def _task(o, l):
        return _fetch_accounts(engine_type, db_name, l, o)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_task, o, l) for o, l in zip(offsets, limits)]
        for fut in as_completed(futures):
            results.extend(fut.result())

    return results


def _fetch_accounts(engine_type: str, db_name: str, limit: int, offset: int) -> List[Dict[str, Any]]:
    if engine_type in ("mysql", "postgres", "sqlserver"):
        return _fetch_sql_rows(engine_type, db_name, limit, offset)
    if engine_type == "mongo":
        return _fetch_mongo_rows(db_name, limit, offset)
    if engine_type == "neo4j":
        return _fetch_neo4j_rows(limit, offset)
    return []
