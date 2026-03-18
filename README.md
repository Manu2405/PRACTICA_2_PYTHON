# Proyecto de ETL y APIs para Bancos Bolivianos

Este proyecto implementa un sistema de **ETL (Extract, Transform, Load)** para procesar datos de cuentas bancarias de 14 bancos bolivianos, con **encriptación de saldos** usando algoritmos criptográficos clásicos y modernos. Además, incluye **14 APIs simuladas** (una por banco) para recepción en tiempo real de cuentas, con autenticación por token y inserción directa en las bases de datos correspondientes.

## 🎯 Contexto y Propósito

- **ETL Batch**: Procesa un archivo CSV (`data/cuentas.csv`) con datos de cuentas, los transforma (calcula saldos en Bs/USD, encripta), y los carga en bases de datos distribuidas (MySQL, PostgreSQL, SQL Server, MongoDB, Neo4j).
- **APIs en Tiempo Real**: Simulan endpoints de bancos para recibir cuentas individuales en tiempo real. Cada API valida un token Bearer, inserta la cuenta en su DB, y devuelve un código de verificación determinista. Ideal para escenarios donde el tipo de cambio fluctúa y se requiere procesamiento inmediato por cuenta.
- **Consumidor Principal**: ASFI (Autoridad de Supervisión del Sistema Financiero) puede enviar cuentas una por una a las APIs, recibiendo confirmación por cada una, permitiendo procesamiento en tiempo real sin batch.

## 🏗️ Arquitectura

### Bases de Datos por Banco
- **MySQL**: `banco_union`, `bcp`, `fortaleza`
- **PostgreSQL**: `mercantil`, `bisa`, `solidario`, `desarrollo_productivo`
- **SQL Server**: `bnb`, `economico`, `fie`
- **MongoDB**: `ganadero`, `prodem`, `pyme_comunidad`
- **Neo4j**: `argentina`

### Encriptación
Cada banco usa un algoritmo específico (ver `services/crypto/`):
- Clásicos: Caesar, Atbash, Vigenère, Playfair, Hill
- Simétricos: DES, 3DES, Blowfish, AES, ChaCha20
- Asimétricos: RSA, ElGamal, ECC

### APIs
- 14 servicios FastAPI independientes (puertos 8881-8894).
- Endpoint `/ingest`: Recibe payload JSON con datos de cuenta, inserta en DB, devuelve código de verificación.
- Autenticación: Bearer token único por banco (en `api/envs/*.env`).

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.8+
- Docker (para bases de datos, ver `docker-compose.yml`)
- Dependencias: `pip install -r requirements.txt`

### Levantar Bases de Datos
```bash
docker-compose up -d
```

### Ejecutar ETL Batch
```bash
python etl/run_etl.py
```

### Ejecutar APIs en Tiempo Real
```bash
python -m api.run_all
```
Las APIs estarán disponibles en `http://127.0.0.1:8881` a `http://127.0.0.1:8894`.

### Ejemplo de Uso de API
```bash
curl -X POST http://127.0.0.1:8881/ingest \
  -H "Authorization: Bearer token_banco_union" \
  -H "Content-Type: application/json" \
  -d '{
    "Nro": "1",
    "Identificacion": "123456",
    "Nombres": "Juan",
    "Apellidos": "Perez",
    "NroCuenta": "000111",
    "IdBanco": "banco_union",
    "SaldoBs": "cifrado_en_bs",
    "SaldoUSD": "cifrado_en_usd"
  }'
```

Respuesta: `{ "verification_code": "..." }`

## 📁 Estructura del Proyecto

- `api/`: APIs simuladas (ver `api/README.md`)
- `etl/`: Lógica de ETL (ver `etl/README.md`)
- `services/`: Servicios de encriptación (ver `services/README.md`)
- `data/`: Datos de entrada (CSV)
- `docker-compose.yml`: Configuración de DBs

## 🔐 Seguridad
- Saldos encriptados antes de inserción.
- Tokens únicos por API para autenticación.
- Códigos de verificación HMAC-SHA256 para integridad.

## 📝 Notas
- El ETL procesa en batch; las APIs en tiempo real.
- Tipo de cambio fijo en ETL (6.96 Bs/USD); en APIs, usar valores pre-calculados.
- Para producción, ajustar configuraciones de DB y cripto.

Para más detalles, ver READMEs en subcarpetas.</content>
<parameter name="filePath">/home/lcoin/Desktop/GIt/SD-Practica2/PRACTICA2/README.md