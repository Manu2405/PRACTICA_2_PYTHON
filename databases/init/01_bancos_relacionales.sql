-- ============================================================================
-- ESQUEMA BASE PARA BANCOS RELACIONALES
-- Proyecto: Plataforma Distribuida de Conversión Monetaria Interbancaria – ASFI
-- Bancos cubiertos aquí:
--   - Banco Unión S.A.        (PostgreSQL)   - IdBanco = 1
--   - Banco Nacional de Bolivia (BNB) (MySQL)   - IdBanco = 3
--   - Banco Fortaleza S.A.    (SQL Server)  - IdBanco = 10
--   - Banco FIE S.A.          (PostgreSQL)  - IdBanco = 11
--
-- NOTA:
-- Cada bloque debe ejecutarse en el motor correspondiente (PostgreSQL,
-- MySQL o SQL Server) usando DBeaver u otro cliente.
-- ============================================================================

-------------------------------------------------------------------------------
-- 1. BANCO UNIÓN S.A. (PostgreSQL)  - BD: db_union
-------------------------------------------------------------------------------
-- Sugerido:
--   CREATE DATABASE db_union;
--   \c db_union;

CREATE TABLE IF NOT EXISTS staging_clientes_union (
    nro            BIGINT,
    identificacion VARCHAR(30),
    nombres        VARCHAR(120),
    apellidos      VARCHAR(120),
    nrocuenta      VARCHAR(30),
    idbanco        INT,
    saldo          NUMERIC(18,4)
);

CREATE TABLE IF NOT EXISTS clientes (
    cliente_id             BIGSERIAL PRIMARY KEY,
    identificacion_cifrada TEXT NOT NULL,
    nombres                VARCHAR(120) NOT NULL,
    apellidos              VARCHAR(120) NOT NULL,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cuentas (
    cuenta_id     BIGSERIAL PRIMARY KEY,
    cliente_id    BIGINT NOT NULL REFERENCES clientes(cliente_id),
    nro_cuenta    VARCHAR(30) NOT NULL UNIQUE,
    saldo_cifrado TEXT NOT NULL,
    moneda        VARCHAR(10) NOT NULL DEFAULT 'USD',
    estado        VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seguridad_cuenta (
    seguridad_id      BIGSERIAL PRIMARY KEY,
    cuenta_id         BIGINT NOT NULL REFERENCES cuentas(cuenta_id),
    algoritmo_cifrado VARCHAR(50) NOT NULL,
    key_id            VARCHAR(100) NOT NULL,
    iv_nonce          VARCHAR(255),
    tag_auth          VARCHAR(255),
    version_cifrado   VARCHAR(20) DEFAULT 'v1',
    fecha_cifrado     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS envios_asfi (
    envio_id           BIGSERIAL PRIMARY KEY,
    cuenta_id          BIGINT NOT NULL REFERENCES cuentas(cuenta_id),
    fecha_envio        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_envio       VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    hash_integridad    VARCHAR(255),
    codigo_verificacion VARCHAR(8),
    respuesta_asfi     TEXT
);

CREATE INDEX IF NOT EXISTS idx_union_clientes_identificacion ON clientes(identificacion_cifrada);
CREATE INDEX IF NOT EXISTS idx_union_cuentas_cliente         ON cuentas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_union_seguridad_cuenta        ON seguridad_cuenta(cuenta_id);
CREATE INDEX IF NOT EXISTS idx_union_envios_cuenta           ON envios_asfi(cuenta_id);


-------------------------------------------------------------------------------
-- 2. BANCO NACIONAL DE BOLIVIA (BNB) - MariaDB  - BD: db_bnb
-------------------------------------------------------------------------------
-- Sugerido:
--   CREATE DATABASE db_bnb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--   USE db_bnb;

CREATE TABLE IF NOT EXISTS staging_clientes_bnb (
    nro            BIGINT,
    identificacion VARCHAR(30),
    nombres        VARCHAR(120),
    apellidos      VARCHAR(120),
    nrocuenta      VARCHAR(30),
    idbanco        INT,
    saldo          DECIMAL(18,4)
);

CREATE TABLE IF NOT EXISTS clientes (
    cliente_id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    identificacion_cifrada TEXT NOT NULL,
    nombres                VARCHAR(120) NOT NULL,
    apellidos              VARCHAR(120) NOT NULL,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cuentas (
    cuenta_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_id    BIGINT NOT NULL,
    nro_cuenta    VARCHAR(30) NOT NULL UNIQUE,
    saldo_cifrado TEXT NOT NULL,
    moneda        VARCHAR(10) NOT NULL DEFAULT 'USD',
    estado        VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bnb_cuentas_clientes FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

CREATE TABLE IF NOT EXISTS seguridad_cuenta (
    seguridad_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    cuenta_id         BIGINT NOT NULL,
    algoritmo_cifrado VARCHAR(50) NOT NULL,
    key_id            VARCHAR(100) NOT NULL,
    iv_nonce          VARCHAR(255),
    tag_auth          VARCHAR(255),
    version_cifrado   VARCHAR(20) DEFAULT 'v1',
    fecha_cifrado     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bnb_seguridad_cuentas FOREIGN KEY (cuenta_id) REFERENCES cuentas(cuenta_id)
);

CREATE TABLE IF NOT EXISTS envios_asfi (
    envio_id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    cuenta_id          BIGINT NOT NULL,
    fecha_envio        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_envio       VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    hash_integridad    VARCHAR(255),
    codigo_verificacion VARCHAR(8),
    respuesta_asfi     TEXT,
    CONSTRAINT fk_bnb_envios_cuentas FOREIGN KEY (cuenta_id) REFERENCES cuentas(cuenta_id)
);

CREATE INDEX idx_bnb_clientes_identificacion ON clientes(identificacion_cifrada(255));
CREATE INDEX idx_bnb_cuentas_cliente         ON cuentas(cliente_id);
CREATE INDEX idx_bnb_seguridad_cuenta        ON seguridad_cuenta(cuenta_id);
CREATE INDEX idx_bnb_envios_cuenta           ON envios_asfi(cuenta_id);


-------------------------------------------------------------------------------
-- 3. BANCO FORTALEZA S.A. (SQL Server)  - BD: db_fortaleza
-------------------------------------------------------------------------------
-- Sugerido:
--   CREATE DATABASE db_fortaleza;
--   GO
--   USE db_fortaleza;
--   GO

IF OBJECT_ID('staging_clientes_fortaleza', 'U') IS NULL
BEGIN
    CREATE TABLE staging_clientes_fortaleza (
        nro            BIGINT,
        identificacion NVARCHAR(30),
        nombres        NVARCHAR(120),
        apellidos      NVARCHAR(120),
        nrocuenta      NVARCHAR(30),
        idbanco        INT,
        saldo          DECIMAL(18,4)
    );
END;
GO

IF OBJECT_ID('clientes', 'U') IS NULL
BEGIN
    CREATE TABLE clientes (
        cliente_id             BIGINT IDENTITY(1,1) PRIMARY KEY,
        identificacion_cifrada NVARCHAR(MAX) NOT NULL,
        nombres                NVARCHAR(120) NOT NULL,
        apellidos              NVARCHAR(120) NOT NULL,
        created_at             DATETIME2 DEFAULT SYSDATETIME()
    );
END;
GO

IF OBJECT_ID('cuentas', 'U') IS NULL
BEGIN
    CREATE TABLE cuentas (
        cuenta_id     BIGINT IDENTITY(1,1) PRIMARY KEY,
        cliente_id    BIGINT NOT NULL,
        nro_cuenta    NVARCHAR(30) NOT NULL UNIQUE,
        saldo_cifrado NVARCHAR(MAX) NOT NULL,
        moneda        NVARCHAR(10) NOT NULL DEFAULT 'USD',
        estado        NVARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
        created_at    DATETIME2 DEFAULT SYSDATETIME(),
        updated_at    DATETIME2 DEFAULT SYSDATETIME(),
        CONSTRAINT fk_fortaleza_cuentas_clientes FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    );
END;
GO

IF OBJECT_ID('seguridad_cuenta', 'U') IS NULL
BEGIN
    CREATE TABLE seguridad_cuenta (
        seguridad_id      BIGINT IDENTITY(1,1) PRIMARY KEY,
        cuenta_id         BIGINT NOT NULL,
        algoritmo_cifrado NVARCHAR(50) NOT NULL,
        key_id            NVARCHAR(100) NOT NULL,
        iv_nonce          NVARCHAR(255),
        tag_auth          NVARCHAR(255),
        version_cifrado   NVARCHAR(20) DEFAULT 'v1',
        fecha_cifrado     DATETIME2 DEFAULT SYSDATETIME(),
        CONSTRAINT fk_fortaleza_seguridad_cuentas FOREIGN KEY (cuenta_id) REFERENCES cuentas(cuenta_id)
    );
END;
GO

IF OBJECT_ID('envios_asfi', 'U') IS NULL
BEGIN
    CREATE TABLE envios_asfi (
        envio_id           BIGINT IDENTITY(1,1) PRIMARY KEY,
        cuenta_id          BIGINT NOT NULL,
        fecha_envio        DATETIME2 DEFAULT SYSDATETIME(),
        estado_envio       NVARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
        hash_integridad    NVARCHAR(255),
        codigo_verificacion NVARCHAR(8),
        respuesta_asfi     NVARCHAR(MAX),
        CONSTRAINT fk_fortaleza_envios_cuentas FOREIGN KEY (cuenta_id) REFERENCES cuentas(cuenta_id)
    );
END;
GO


-------------------------------------------------------------------------------
-- 4. BANCO FIE S.A. (PostgreSQL)  - BD: db_fie
-------------------------------------------------------------------------------
-- Sugerido:
--   CREATE DATABASE db_fie;
--   \c db_fie;

CREATE TABLE IF NOT EXISTS staging_clientes_fie (
    nro            BIGINT,
    identificacion VARCHAR(30),
    nombres        VARCHAR(120),
    apellidos      VARCHAR(120),
    nrocuenta      VARCHAR(30),
    idbanco        INT,
    saldo          NUMERIC(18,4)
);

CREATE TABLE IF NOT EXISTS clientes (
    cliente_id             BIGSERIAL PRIMARY KEY,
    identificacion_cifrada TEXT NOT NULL,
    nombres                VARCHAR(120) NOT NULL,
    apellidos              VARCHAR(120) NOT NULL,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cuentas (
    cuenta_id     BIGSERIAL PRIMARY KEY,
    cliente_id    BIGINT NOT NULL REFERENCES clientes(cliente_id),
    nro_cuenta    VARCHAR(30) NOT NULL UNIQUE,
    saldo_cifrado TEXT NOT NULL,
    moneda        VARCHAR(10) NOT NULL DEFAULT 'USD',
    estado        VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seguridad_cuenta (
    seguridad_id      BIGSERIAL PRIMARY KEY,
    cuenta_id         BIGINT NOT NULL REFERENCES cuentas(cuenta_id),
    algoritmo_cifrado VARCHAR(50) NOT NULL,
    key_id            VARCHAR(100) NOT NULL,
    iv_nonce          VARCHAR(255),
    tag_auth          VARCHAR(255),
    version_cifrado   VARCHAR(20) DEFAULT 'v1',
    fecha_cifrado     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS envios_asfi (
    envio_id           BIGSERIAL PRIMARY KEY,
    cuenta_id          BIGINT NOT NULL REFERENCES cuentas(cuenta_id),
    fecha_envio        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_envio       VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    hash_integridad    VARCHAR(255),
    codigo_verificacion VARCHAR(8),
    respuesta_asfi     TEXT
);

CREATE INDEX IF NOT EXISTS idx_fie_clientes_identificacion ON clientes(identificacion_cifrada);
CREATE INDEX IF NOT EXISTS idx_fie_cuentas_cliente         ON cuentas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_fie_seguridad_cuenta        ON seguridad_cuenta(cuenta_id);
CREATE INDEX IF NOT EXISTS idx_fie_envios_cuenta           ON envios_asfi(cuenta_id);

