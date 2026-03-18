from neo4j import GraphDatabase
from etl.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def insert_neo4j(row):

    with driver.session() as session:

        session.run(
            """
            MERGE (c:Cliente {ci:$ci})
            SET c.nombre=$nombre,
                c.apellido=$apellido

            MERGE (a:Cuenta {numero:$cuenta})
            SET a.saldo=$saldo,
                a.banco=$banco,
                a.nro=$nro

            MERGE (c)-[:TIENE]->(a)
            """,
            ci=row["Identificacion"],
            nombre=row["Nombres"],
            apellido=row["Apellidos"],
            cuenta=row["NroCuenta"],
            saldo=row["Saldo"],
            banco=row["IdBanco"],
            nro=row["Nro"]
        )


def insert_neo4j_batch(rows):
    """Insert multiple rows into Neo4j in one transaction."""

    if not rows:
        return

    params = [
        {
            "ci": r["Identificacion"],
            "nombre": r["Nombres"],
            "apellido": r["Apellidos"],
            "cuenta": r["NroCuenta"],
            "saldo": r["Saldo"],
            "banco": r["IdBanco"],
            "nro": r["Nro"],
        }
        for r in rows
    ]

    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MERGE (c:Cliente {ci: row.ci})
            SET c.nombre = row.nombre,
                c.apellido = row.apellido

            MERGE (a:Cuenta {numero: row.cuenta})
            SET a.saldo = row.saldo,
                a.banco = row.banco,
                a.nro = row.nro

            MERGE (c)-[:TIENE]->(a)
            """,
            rows=params,
        )
