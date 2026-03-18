# ASFI Central Service

El Servicio Central de ASFI (Autoridad de Supervisión del Sistema Financiero) es un sistema automatizado que recopila datos de cuentas bancarias de 14 bancos bolivianos en tiempo real. El servicio:

- **Recopila datos**: Consulta las APIs de cada banco para obtener información de cuentas encriptadas.
- **Desencripta**: Usa algoritmos específicos por banco para desencriptar los datos sensibles.
- **Convierte saldos**: Obtiene el tipo de cambio USD/BOB del simulador BCB y calcula saldos en ambas monedas.
- **Almacena centralmente**: Inserta los datos desencriptados en una base de datos MySQL central (`asfi_central`).
- **Genera verificaciones**: Crea y envía códigos de verificación únicos por cuenta a cada banco.
- **Registra logs**: Mantiene un registro detallado de todas las operaciones con timestamps.

## Arquitectura

El servicio está diseñado para ser eficiente y escalable:

- **Programación asíncrona**: Usa `asyncio` y `httpx` para consultas concurrentes a las 14 APIs bancarias y al BCB, maximizando el uso de recursos.
- **Paralelismo**: Todas las llamadas a bancos se ejecutan en paralelo para minimizar el tiempo total de recopilación.
- **Desencriptación**: Soporta múltiples algoritmos criptográficos (clásicos, simétricos, asimétricos) según el banco.
- **Persistencia**: Usa SQLAlchemy para inserciones seguras en MySQL con manejo de conflictos (ON DUPLICATE KEY UPDATE).
- **Logs**: Registra operaciones críticas con timestamps, tipos de cambio, IDs de cuenta y banco, algoritmos usados, etc.

## Requisitos

- Python 3.8+
- MySQL 8.0+ (para `asfi_central`)
- Acceso a las APIs bancarias (puertos 8881-8894)
- Simulador BCB (puerto 8001)
- Dependencias: `pip install -r requirements.txt`

## Configuración

### Base de Datos ASFI Central

Crear la base de datos MySQL `asfi_central` y las tablas:

```sql
CREATE DATABASE asfi_central;

USE asfi_central;

-- Tabla de Bancos (ya poblada)
CREATE TABLE Bancos (
    BancoId INT PRIMARY KEY,
    Nombre VARCHAR(100),
    AlgoritmoEncriptacion VARCHAR(50)
);

-- Insertar bancos (ejemplo)
INSERT INTO Bancos VALUES
(1, 'Banco Unión S.A.', 'Cifrado Cesar'),
(2, 'Banco Mercantil Santa Cruz S.A.', 'Atbash'),
-- ... (completar con los 14 bancos)

-- Tabla de Cuentas
CREATE TABLE Cuentas (
    Nro BIGINT PRIMARY KEY,
    Identificacion VARCHAR(20),
    Nombres VARCHAR(100),
    Apellidos VARCHAR(100),
    NroCuenta VARCHAR(30),
    BancoId INT,
    SaldoUSD DECIMAL(18,4),
    SaldoBs DECIMAL(18,4),
    CodigoVerificacion CHAR(8),
    CreatedAt DATETIME,
    CreatedBy VARCHAR(50),
    FOREIGN KEY (BancoId) REFERENCES Bancos(BancoId)
);
```

### Variables de Entorno

Copiar `asfi/envs/.env.example` a `asfi/envs/.env` y configurar:

```bash
# Conexión MySQL para ASFI
ASFI_DB_USER=root
ASFI_DB_PASSWORD=root123
ASFI_DB_HOST=localhost
ASFI_DB_PORT=3306
ASFI_DB_NAME=asfi_central

# Endpoint del simulador BCB
BCB_URL=http://127.0.0.1:8001/rate

# Tokens para cada API bancaria
TOKEN_BANCO_UNION=token_banco_union
TOKEN_BCP=token_bcp
# ... (uno por banco)

# Claves privadas para desencriptación asimétrica (opcional)
RSA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
ECC_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
ELGAMAL_PRIVATE_KEY=""  # No usado por defecto
```

### Claves de Desencriptación

Para algoritmos asimétricos (RSA, ECC), proporcionar las claves privadas correspondientes. Si no se proporcionan, el servicio registra una advertencia y deja el campo encriptado.

## Uso

### Ejecución Única

Para una ejecución puntual:

```bash
cd asfi
python -m main --once --log-file ingestion.log
```

### Ejecución Continua

Para monitoreo en tiempo real cada 30 segundos:

```bash
cd asfi
python -m main --interval 30 --log-file asfi.log
```

### Opciones

- `--once`: Ejecuta una sola vez y sale.
- `--interval N`: Ejecuta en bucle cada N segundos.
- `--log-file PATH`: Archivo opcional para logs (además de stdout).

## Flujo de Operación

1. **Consulta Tipo de Cambio**: Obtiene el rate USD/BOB del BCB.
2. **Recopilación Paralela**: Llama a las 14 APIs bancarias concurrentemente para obtener una cuenta por banco.
3. **Desencriptación**: Para cada cuenta, consulta el algoritmo del banco en `Bancos` y desencripta campos sensibles (Identificación, Nombres, etc.).
4. **Cálculo de Saldos**: Convierte el saldo USD a Bs usando el rate actual.
5. **Generación de Verificación**: Crea un código único de 8 caracteres por cuenta.
6. **Envío de Verificación**: POST al endpoint `/verify` del banco correspondiente.
7. **Almacenamiento**: Inserta/actualiza en `Cuentas` con logs detallados.
8. **Logging**: Registra timestamp, rate usado, Nro, BancoId, algoritmo, saldos, etc.

## Logs

Los logs incluyen:

- Timestamp de operación.
- Tipo de cambio USD/BOB usado.
- Nro de cuenta.
- BancoId.
- Algoritmo de encriptación.
- Saldos calculados (USD y Bs).
- Estado de desencriptación (éxito/error).
- Códigos de verificación generados.

Ejemplo de log:

```
2026-03-17 12:00:00 INFO Using USD/BOB rate 6.9600
2026-03-17 12:00:01 INFO Stored account Nro=20617 BancoId=5 rate=6.9600 saldo_usd=3499999.2130 saldo_bs=24335995.0829 algo=Hill
2026-03-17 12:00:02 INFO Verification sent to bank bisa: code=ABC12345 for account 20617
```

## Eficiencia y Paralelismo

- **Asyncio**: Todas las I/O operations (HTTP calls) son asíncronas.
- **Concurrencia**: 14 llamadas a bancos + 1 a BCB en paralelo.
- **Timeouts**: Configurados para evitar bloqueos (10s por banco, 5s por BCB).
- **Pooling**: SQLAlchemy maneja conexiones eficientemente.
- **Batch Inserts**: Aunque por cuenta, usa transacciones para atomicidad.

## Verificaciones

Por cada cuenta procesada:

- Genera un código único (8 caracteres alfanuméricos aleatorios).
- Envía vía POST a `{bank_url}/verify` con payload:

```json
{
  "items": [
    {
      "NroCuenta": "123456789",
      "verification_code": "ABC12345"
    }
  ]
}
```

- Registra el envío en logs (éxito o fallo).

## Manejo de Errores

- Si falla una API bancaria: Log warning, continúa con otros bancos.
- Si falla BCB: Aborta la ejecución completa.
- Si falla desencriptación: Almacena datos encriptados, log error.
- Si falla inserción DB: Retry con backoff (no implementado aún).

## Desarrollo

Para contribuir:

1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar `.env` local.
3. Ejecutar tests: `python -m pytest` (si se agregan).
4. Seguir PEP 8 y usar type hints.

## Notas

- El servicio asume que las APIs bancarias están corriendo (ver `api/run_all.py`).
- El simulador BCB debe estar activo (ver `services/bcb_simulator`).
- Para producción, usar HTTPS, autenticación robusta, y monitoreo (e.g., Prometheus).</content>
<parameter name="filePath">/home/lcoin/Desktop/GIt/SD-Practica2/PRACTICA2/asfi/README.md