# Banco API Simulators

This folder contains a simple FastAPI-based simulator for 14 bank APIs.
Each bank API:

- Runs on its own HTTP port (8881..8894)
- Requires a specific Bearer token (configured in `api/envs/*.env`)
- Exposes `/accounts` (GET) to deliver account data from its connected database
- Exposes `/verify` (POST) to accept verification codes from ASFI and record them
- Exposes `/verifications` (GET) to inspect received verification codes
- Exposes `/health` for basic liveness checks

## Running All APIs (parallel)

From the project root:

```bash
python -m api.run_all
```

Each bank will start on:

- `banco_union` → http://127.0.0.1:8881
- `bcp` → http://127.0.0.1:8882
- ...
- `argentina` → http://127.0.0.1:8894

Press `Ctrl+C` to stop all servers.

## Calling an API

### 1) Fetch account data (GET)

Request:

- `GET /accounts`
- Requires `Authorization: Bearer <TOKEN>`
- Optional query params:
  - `limit` (default 100)
  - `offset` (default 0)
  - `parallel` (default `false`)
  - `workers` (default 4)

Response:

```json
{
  "accounts": [
    {
      "Nro": "...",
      "Identificacion": "...",
      "Nombres": "...",
      "Apellidos": "...",
      "NroCuenta": "...",
      "IdBanco": "...",
      "SaldoBs": "...",
      "SaldoUSD": "..."
    }
  ]
}
```

### 2) Send verification codes back (POST)

Request:

- `POST /verify`
- Requires `Authorization: Bearer <TOKEN>`
- JSON body:

```json
{
  "items": [
    { "NroCuenta": "...", "verification_code": "..." }
  ]
}
```

Response:

```json
{ "accepted": 1, "rejected": 0 }
```

### 3) Inspect what codes were received

- `GET /verifications`
- Returns a map of `NroCuenta` → verification metadata
