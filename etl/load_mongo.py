from pymongo import MongoClient
from etl.config import MONGO_URI


client = MongoClient(MONGO_URI)


def insert_mongo(db_name, row):

    db = client[db_name]

    collection = db["cuentas"]

    collection.insert_one(row)


def insert_mongo_batch(db_name, rows, ordered: bool = False):
    """Insert many documents into MongoDB in a single round-trip."""

    db = client[db_name]
    collection = db["cuentas"]

    if not rows:
        return

    collection.insert_many(rows, ordered=ordered)
