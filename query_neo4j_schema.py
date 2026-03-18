from neo4j import GraphDatabase
from etl.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # Get one node of type Cuenta
        result = session.run("MATCH (c:Cuenta) RETURN labels(c) as labels, keys(c) as keys LIMIT 1")
        for record in result:
            print(f"Cuenta Node Labels: {record['labels']}")
            print(f"Cuenta Node Keys: {record['keys']}")

        # Get relationships from Cuenta
        result = session.run("MATCH (c:Cuenta)-[r]-(n) RETURN type(r) as rel_type, labels(n) as node_labels LIMIT 1")
        for record in result:
            print(f"Relationship: {record['rel_type']}, Target Node Labels: {record['node_labels']}")
            
        # Get one node of type Cliente
        result = session.run("MATCH (c:Cliente) RETURN labels(c) as labels, keys(c) as keys LIMIT 1")
        for record in result:
            print(f"Cliente Node Labels: {record['labels']}")
            print(f"Cliente Node Keys: {record['keys']}")

            
if __name__ == '__main__':
    main()
