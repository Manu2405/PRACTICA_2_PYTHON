## Guía rápida para TOCO – Simulador BCB y cambio de tipo de cambio

Este documento resume **solo** la parte del simulador BCB y cómo demostrar
que el **tipo de cambio se actualiza automáticamente cada cierto tiempo**.

---

## 1. Dónde está el simulador BCB

- Carpeta del proyecto: `PRACTICA_2_PYTHON`
- Servicio: `bcb-simulator`
- Archivo de configuración: `bcb-simulator/config.py`
- Lógica principal: `bcb-simulator/main.py`

El simulador es un microservicio FastAPI que expone:

- `GET /rate` en `http://localhost:8000/rate`

---

## 2. Parámetros importantes (configuración)

En `bcb-simulator/config.py`:

- **`BASE_RATE`**: tipo de cambio base publicado por el BCB (ej. `6.96`).
- **`MAX_DELTA`**: oscilación máxima permitida alrededor de la base (`±0.9999`).
- **`REFRESH_SECONDS`**: cada cuántos segundos se refresca el tipo de cambio.
- **`SEED`**: semilla opcional para pruebas reproducibles.

Estos valores se pueden sobreescribir con variables de entorno que
ya están definidas en `docker-compose.yml`:

```yaml
environment:
  - BCB_BASE_RATE=6.96
  - BCB_MAX_DELTA=0.9999
  - BCB_REFRESH_SECONDS=180
```

> Para las demos podemos bajar `BCB_REFRESH_SECONDS` a algo como `10` segundos
> para ver cambios más rápidos.

---

## 3. Algoritmo del tipo de cambio

En `bcb-simulator/main.py`:

1. **Generación de una nueva tasa**:

```python
def generate_rate(previous_rate: Decimal | None = None) -> Decimal:
    base = settings.BASE_RATE
    ref = previous_rate or base

    # Variación aleatoria en [-MAX_DELTA, +MAX_DELTA]
    delta_float = random.uniform(float(-settings.MAX_DELTA), float(settings.MAX_DELTA))
    raw_rate = ref + Decimal(str(delta_float))

    # Se fuerza a estar dentro de [base - MAX_DELTA, base + MAX_DELTA]
    # y se deja con 4 decimales fijos.
    return clamp_rate(raw_rate, base=base, max_delta=settings.MAX_DELTA)
```

- Si no hay valor previo, parte de la **tasa base (`BASE_RATE`)**.
- En cada refresco aplica una variación pseudoaleatoria controlada.
- `clamp_rate` se asegura de:
  - No salir del rango \[BASE\_RATE − MAX\_DELTA, BASE\_RATE + MAX\_DELTA\].
  - Mantener **4 decimales** usando `Decimal("0.0001")`.

2. **Refresco por tiempo**:

```python
def _maybe_refresh_rate() -> None:
    global _current_rate, _last_update

    now = datetime.now(timezone.utc)

    if _current_rate is None or _last_update is None:
        _current_rate = generate_rate()
        _last_update = now
        return

    elapsed = (now - _last_update).total_seconds()
    if elapsed >= settings.REFRESH_SECONDS:
        _current_rate = generate_rate(previous_rate=_current_rate)
        _last_update = now
```

- Se guarda el último valor `_current_rate` y el momento `_last_update`.
- Solo cuando han pasado al menos `REFRESH_SECONDS` segundos se genera
  una **nueva** tasa.

3. **Endpoint `/rate`**:

```python
@app.get("/rate")
def get_rate():
    _maybe_refresh_rate()

    return {
        "rate": str(_current_rate),
        "base_rate": str(settings.BASE_RATE),
        "max_delta": str(settings.MAX_DELTA),
        "refreshed_at": _last_update.isoformat(),
        "refresh_seconds": settings.REFRESH_SECONDS,
    }
```

La respuesta incluye:

- `rate`: tipo de cambio actual (string con 4 decimales).
- `base_rate`: tasa base configurada.
- `max_delta`: oscilación máxima.
- `refreshed_at`: fecha/hora UTC de la última actualización.
- `refresh_seconds`: intervalo de refresco efectivo.

---

## 4. Cómo levantar el simulador BCB

Desde la raíz del proyecto:

```bash
docker compose up -d bcb-simulator
```

O desde Docker Desktop arrancando el contenedor `bcb-simulator`
que pertenece al stack `practica_2_python`.

Para comprobar que está arriba:

- Abrir `http://localhost:8000/docs` en el navegador.
- Probar el endpoint `GET /rate`.

---

## 5. Cómo demostrar que el tipo de cambio cambia cada X segundos

### Paso 1: Ajustar el intervalo (opcional, para la demo)

Editar `docker-compose.yml` y poner, por ejemplo:

```yaml
BCB_REFRESH_SECONDS=10
```

Volver a levantar el servicio:

```bash
docker compose down
docker compose up -d bcb-simulator
```

### Paso 2: Observar el comportamiento en `/rate`

1. Ir a `http://localhost:8000/docs`.
2. Abrir `GET /rate` y hacer **Execute** varias veces seguidas:
   - Durante ~10 segundos, el campo `rate` se mantiene igual.
   - También el campo `refreshed_at` se mantiene igual.
3. Esperar unos segundos más (hasta pasar los 10 s).
4. Volver a hacer **Execute**:
   - El campo `rate` muestra un **nuevo valor** dentro del rango permitido.
   - El campo `refreshed_at` cambia a un timestamp más reciente.

Con esto se demuestra claramente:

- Que el tipo de cambio **no es fijo**, sino que se actualiza según un algoritmo.
- Que el intervalo de refresco es **parametrizable** con `BCB_REFRESH_SECONDS`.
- Que se usa `Decimal` con 4 decimales y un rango controlado alrededor del valor base.

---

## 6. Relación con ASFI y BNB

- La API central de ASFI consulta este tipo de cambio con la función
  `fetch_current_rate` (cliente HTTP).
- Cada vez que se llama a `POST /asfi/conversion`, ASFI usa el valor
  actual de `rate` para convertir `saldo_usd` → `saldo_bs`.
- Para BNB (y los demás bancos), esto garantiza que la conversión
  siempre se hace con el **tipo de cambio oficial actualizado** que
  estamos simulando con este servicio.

