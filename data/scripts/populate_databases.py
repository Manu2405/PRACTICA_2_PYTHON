"""
Script para preparar los datos de entrada a partir del dataset original de ASFI.

FUNCIONALIDAD ACTUAL:
    - Lee el archivo CSV maestro con todas las cuentas.
    - Filtra por IdBanco y genera 4 archivos independientes:
        - data/union.csv      (IdBanco = 1)
        - data/bnb.csv        (IdBanco = 3)
        - data/fortaleza.csv  (IdBanco = 10)
        - data/fie.csv        (IdBanco = 11)

    Cada CSV se puede importar luego a las tablas staging:
        - staging_clientes_union      (PostgreSQL - Unión)
        - staging_clientes_bnb        (MariaDB   - BNB)
        - staging_clientes_fortaleza  (SQLServer - Fortaleza)
        - staging_clientes_fie        (PostgreSQL - FIE)

NOTA:
    Este script NO se conecta todavía a las bases de datos. Su objetivo es
    preparar archivos limpios por banco para que la importación sea sencilla
    usando DBeaver (COPY, LOAD DATA, BULK INSERT, etc.).
"""

from pathlib import Path
import csv


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"

# Nombre del archivo maestro (ajusta si tu archivo se llama distinto)
MASTER_CSV = DATA_DIR / "01_Practica2_Dataset.csv"


BANCOS_MAP = {
    "1": "union",
    "3": "bnb",
    "10": "fortaleza",
    "11": "fie",
}


def split_dataset() -> None:
    if not MASTER_CSV.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo maestro: {MASTER_CSV}\n"
            "Copia el dataset original a la carpeta 'data' con ese nombre "
            "o ajusta la constante MASTER_CSV en este script."
        )

    DATA_DIR.mkdir(exist_ok=True, parents=True)

    outputs = {name: open(DATA_DIR / f"{name}.csv", "w", newline="", encoding="utf-8") for name in BANCOS_MAP.values()}
    writers = {}

    try:
        with MASTER_CSV.open("r", newline="", encoding="utf-8") as f_in:
            reader = csv.DictReader(f_in)

            # Prepara un writer por banco, con el mismo header
            for banco_nombre, file in outputs.items():
                writers[banco_nombre] = None  # se inicializa cuando haya header

            for row in reader:
                id_banco = row.get("IdBanco")
                if id_banco is None:
                    continue

                banco_nombre = BANCOS_MAP.get(str(id_banco))
                if not banco_nombre:
                    continue

                writer = writers[banco_nombre]
                if writer is None:
                    writer = csv.DictWriter(outputs[banco_nombre], fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writers[banco_nombre] = writer

                writer.writerow(row)

    finally:
        for file in outputs.values():
            file.close()


if __name__ == "__main__":
    split_dataset()
    print("Archivos generados en 'data/': union.csv, bnb.csv, fortaleza.csv, fie.csv")

