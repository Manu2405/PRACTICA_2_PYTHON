# ETL Module

Este módulo maneja el proceso de **ETL (Extract, Transform, Load)** para datos de cuentas bancarias.

## Componentes

- `run_etl.py`: Orquestador principal. Extrae de CSV, transforma (encripta), carga en DBs en paralelo.
- `extract.py`: Lee `data/cuentas.csv`.
- `transform.py`: Calcula saldos Bs/USD, encripta usando `crypto_router.py`.
- `load_*.py`: Loaders específicos por tipo de DB (MySQL, Postgres, etc.).
- `db_router.py`: Enruta inserciones por banco y tipo de DB.
- `crypto_router.py`: Selecciona algoritmo de encriptación por banco.
- `engine_factory.py`: Crea conexiones a DBs.

## Ejecución
```bash
python etl/run_etl.py
```

Procesa todas las cuentas del CSV y las inserta en las DBs correspondientes, con saldos encriptados.</content>
<parameter name="filePath">/home/lcoin/Desktop/GIt/SD-Practica2/PRACTICA2/etl/README.md