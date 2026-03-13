-- ============================================================================
-- ESQUEMA BASE CENTRAL ASFI (PostgreSQL)
-- BD sugerida: db_asfi
-- ============================================================================

-- Sugerido:
--   CREATE DATABASE db_asfi;
--   \c db_asfi;

CREATE TABLE IF NOT EXISTS bancos (
    banco_id        INT PRIMARY KEY,
    nombre_banco    VARCHAR(150) NOT NULL,
    motor_bd        VARCHAR(50)  NOT NULL,
    algoritmo_cifrado VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS cuentas_origen (
    origen_id              BIGSERIAL PRIMARY KEY,
    banco_id               INT NOT NULL REFERENCES bancos(banco_id),
    cuenta_id_externa      BIGINT NOT NULL,
    identificacion_descifrada VARCHAR(30) NOT NULL,
    nro_cuenta             VARCHAR(30) NOT NULL,
    saldo_usd              NUMERIC(18,4) NOT NULL,
    fecha_recepcion        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversiones (
    conversion_id     BIGSERIAL PRIMARY KEY,
    origen_id         BIGINT NOT NULL REFERENCES cuentas_origen(origen_id),
    tipo_cambio       NUMERIC(10,4) NOT NULL,
    saldo_bs          NUMERIC(18,4) NOT NULL,
    fecha_conversion  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    codigo_verificacion VARCHAR(8) NOT NULL
);

CREATE TABLE IF NOT EXISTS auditoria (
    auditoria_id        BIGSERIAL PRIMARY KEY,
    timestamp_evento    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    banco_id            INT NOT NULL,
    cuenta_id_externa   BIGINT NOT NULL,
    tipo_cambio_aplicado NUMERIC(10,4),
    hash_integridad     VARCHAR(255),
    resultado           VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS validaciones (
    validacion_id   BIGSERIAL PRIMARY KEY,
    conversion_id   BIGINT NOT NULL REFERENCES conversiones(conversion_id),
    saldo_banco_bs  NUMERIC(18,4),
    saldo_asfi_bs   NUMERIC(18,4),
    coincide        BOOLEAN,
    fecha_validacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_asfi_cuentas_origen_banco    ON cuentas_origen(banco_id);
CREATE INDEX IF NOT EXISTS idx_asfi_conversiones_origen     ON conversiones(origen_id);
CREATE INDEX IF NOT EXISTS idx_asfi_auditoria_banco_cuenta  ON auditoria(banco_id, cuenta_id_externa);
CREATE INDEX IF NOT EXISTS idx_asfi_validaciones_conversion ON validaciones(conversion_id);

-- Registro de los 4 bancos relacionales utilizados en este proyecto
INSERT INTO bancos (banco_id, nombre_banco, motor_bd, algoritmo_cifrado)
VALUES
    (1,  'Banco Unión S.A.',                            'PostgreSQL', 'Cesar'),
    (3,  'Banco Nacional de Bolivia S.A. (BNB)',        'MariaDB',    'Vigenere'),
    (10, 'Banco Fortaleza S.A.',                        'SQL Server', 'AES'),
    (11, 'Banco FIE S.A.',                              'PostgreSQL', 'RSA')
ON CONFLICT (banco_id) DO NOTHING;

