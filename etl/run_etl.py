import os
import sys
from concurrent.futures import ProcessPoolExecutor

# Ensure the repository root is on sys.path so this module can be executed both:
#  - python3 etl/run_etl.py
#  - python3 -m etl.run_etl
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from etl.extract import extract_csv
from etl.transform import transform_row
from etl.db_router import route_insert_many
from tqdm import tqdm


def run():

    # Use the supplied dataset file. The repository ships with data/cuentas.csv.
    data = extract_csv("data/cuentas.csv")

    # Transform data in parallel using processes
    with ProcessPoolExecutor() as executor:
        transformed = list(tqdm(executor.map(transform_row, data), total=len(data), desc="Transformando datos"))

    print("Primeros registros transformados:\n")
    for r in transformed[:5]:
        print(r)

    # Carga en batch hacia las 14 bases de datos, agrupando por motor y base de datos.
    route_insert_many(transformed)


if __name__ == "__main__":
    run()
