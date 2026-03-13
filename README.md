## Plataforma Distribuida de Conversión Monetaria Interbancaria – ASFI

Backend de práctica de Sistemas Distribuidos. No tiene frontend.

- **Tecnologías principales**:
  - Python 3.11
  - FastAPI
  - PostgreSQL, MySQL, SQL Server
  - asyncpg, httpx
  - Docker + Docker Compose (simulador BCB)

---

## 1. Requisitos previos

- Python 3.11 instalado y agregado al `PATH`.
- Docker Desktop instalado y en ejecución.
- Motores de BD instalados:
  - PostgreSQL (para Banco Unión, Banco FIE y ASFI central).
  - MySQL (para BNB).
  - SQL Server (para Banco Fortaleza).
- Git configurado y clon del repositorio en esta máquina.

---

## 2. Instalación de dependencias (entorno local)

Desde la carpeta raíz del proyecto:

```bash
cd PRACTICA_2_PYTHON
pip install -r requirements.txt
```

> Nota: Las versiones de `fastapi`, `uvicorn` y `pydantic` ya están fijadas para evitar problemas de compatibilidad.

---

## 3. Bases de datos

### 3.1. Crear y cargar ASFI (`db_asfi` – PostgreSQL)

1. Crear la base de datos `db_asfi` en PostgreSQL (por ejemplo con pgAdmin).
2. Ejecutar el script:

```sql
-- En PostgreSQL, conectados a db_asfi
\i databases/init/03_asfi_central.sql
```

Esto crea las tablas:
- `bancos`
- `cuentas_origen`
- `conversiones`
- `auditoria`
- `validaciones`

Y registra los 4 bancos en `bancos`.

### 3.2. Bancos relacionales

Los DDL para los 4 bancos están en:

- `databases/init/01_bancos_relacionales.sql`

El dataset maestro está en `data/01_Practica2_Dataset.csv`.
El script `data/scripts/populate_databases.py` genera:

- `data/union.csv`
- `data/bnb.csv`
- `data/fortaleza.csv`
- `data/fie.csv`

Esos CSV se importan en las tablas `staging_clientes_*` de cada motor
con las herramientas gráficas (pgAdmin, DBeaver, SSMS, etc.).

---

## 4. Simulador BCB (tipo de cambio)

Este servicio es un microservicio FastAPI dentro de la carpeta `bcb-simulator`.

### 4.1. Levantar con Docker Compose

Desde la raíz del proyecto:

```bash
docker compose up -d bcb-simulator
```

Si ya está construido, también puedes iniciarlo desde Docker Desktop.

### 4.2. Probar el simulador

Ir en el navegador a:

- `http://localhost:8000/docs`

Deberías ver la documentación de FastAPI con el endpoint:

- `GET /rate`

La respuesta incluye:
- `rate`: tipo de cambio USD→Bs con 4 decimales.
- `base_rate`, `max_delta`, `refreshed_at`, `refresh_seconds`.

---

## 5. API central ASFI

### 5.1. Configuración

Las variables principales están en `asfi/config.py`:

- `ASFI_DB_DSN`: cadena de conexión a `db_asfi`.
- `BCB_BASE_URL`: URL del simulador BCB (por defecto `http://localhost:8000`).
- `PRECISION_DECIMALES`: número de decimales para montos y tipo de cambio.

### 5.2. Levantar ASFI

Desde la raíz del proyecto:

```bash
python -m uvicorn asfi.main:app --reload --port 8001
```

Swagger UI de ASFI:

- `http://127.0.0.1:8001/docs`

### 5.3. Endpoint principal: `/asfi/conversion`

- **Método**: `POST`
- **URL completa**: `http://127.0.0.1:8001/asfi/conversion`
- **Descripción**: Registra una conversión USD→Bs para una cuenta de un banco.

#### Body de ejemplo (JSON)

```json
{
  "banco_id": 1,
  "cuenta_id_externa": 123456,
  "identificacion": "5977236805",
  "nro_cuenta": "64098024299780150",
  "saldo_usd": 1000.1234
}
```

#### Parámetros (explicación)

- `banco_id`: ID del banco según tabla `bancos` de ASFI.
- `cuenta_id_externa`: identificador de la cuenta en el banco origen.
- `identificacion`: CI/NIT del cliente ya descifrado.
- `nro_cuenta`: número de cuenta en el banco origen.
- `saldo_usd`: saldo en dólares estadounidenses que se va a convertir.

#### Respuesta de ejemplo

```json
{
  "banco_id": 1,
  "cuenta_id_externa": 123456,
  "saldo_usd": 1000.1234,
  "tipo_cambio": 7.0599,
  "saldo_bs": 7969.8823,
  "codigo_verificacion": "E9ED1C7B",
  "timestamp": "2026-03-13T18:17:51.032604"
}
```

Campos de salida:

- `tipo_cambio`: tipo de cambio obtenido del simulador BCB.
- `saldo_bs`: monto en bolivianos calculado y redondeado.
- `codigo_verificacion`: código único para trazabilidad.
- `timestamp`: momento de registro en ASFI.

---

## 6. Trazabilidad en la base de datos ASFI

Después de llamar a `POST /asfi/conversion`, se registran filas en:

- `cuentas_origen`
- `conversiones`
- `auditoria`

Ejemplos de consultas útiles (en `db_asfi`):

```sql
SELECT * FROM cuentas_origen ORDER BY origen_id DESC;

SELECT * FROM conversiones ORDER BY conversion_id DESC;

SELECT
    co.origen_id,
    co.banco_id,
    co.cuenta_id_externa,
    co.identificacion_descifrada,
    co.nro_cuenta,
    co.saldo_usd,
    co.fecha_recepcion,
    c.conversion_id,
    c.tipo_cambio,
    c.saldo_bs,
    c.fecha_conversion,
    c.codigo_verificacion,
    a.auditoria_id,
    a.timestamp_evento,
    a.tipo_cambio_aplicado,
    a.hash_integridad,
    a.resultado
FROM cuentas_origen co
JOIN conversiones c ON c.origen_id = co.origen_id
JOIN auditoria a ON a.banco_id = co.banco_id
                 AND a.cuenta_id_externa = co.cuenta_id_externa
ORDER BY c.conversion_id DESC;
```

---

## 7. Flujo mínimo para probar todo

1. PostgreSQL: crear `db_asfi` y ejecutar `databases/init/03_asfi_central.sql`.
2. Generar y cargar datos en los bancos desde `data/01_Practica2_Dataset.csv`
   usando `data/scripts/populate_databases.py` y las herramientas gráficas.
3. Levantar el simulador BCB:
   ```bash
   docker compose up -d bcb-simulator
   ```
4. Levantar ASFI:
   ```bash
   python -m uvicorn asfi.main:app --reload --port 8001
   ```
5. Ir a `http://127.0.0.1:8001/docs` y probar `POST /asfi/conversion`
   con un body como el del ejemplo.
6. Verificar en `db_asfi` que aparezcan las filas correspondientes en
   `cuentas_origen`, `conversiones` y `auditoria`.

