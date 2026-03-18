from neo4j import GraphDatabase
from etl.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # Check relation direction
        result = session.run("MATCH (c:Cuenta)-[r]->(n) RETURN labels(c), type(r), labels(n) LIMIT 1")
        for record in result:
            print("Direction 1 (Cuenta -> n):", record)
            
        result = session.run("MATCH (n)-[r]->(c:Cuenta) RETURN labels(n), type(r), labels(c) LIMIT 1")
        for record in result:
            print("Direction 2 (n -> Cuenta):", record)
            
        # Test my query
        print("Testing query without direction...")
        result = session.run(
            """
            MATCH (cl:Cliente)-[:TIENE]-(c:Cuenta)
            RETURN 
                c.nro AS Nro, 
                cl.ci AS Identificacion,
                cl.nombre AS Nombres,
                cl.apellido AS Apellidos,
                c.numero AS NroCuenta,
                c.banco AS IdBanco,
                c.saldo AS SaldoUSD
            ORDER BY c.nro
            LIMIT 1
            """
        )
        for record in result:
            print("Query Result:", dict(record))

if __name__ == '__main__':
    main()
