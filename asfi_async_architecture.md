# Arquitectura Asíncrona en el Servicio ASFI Central

El Servicio Central de ASFI se encarga de recopilar información bancaria cifrada de las 14 entidades financieras, hacer conversiones monetarias, insertar estos registros en una base centralizada (MySQL) del gobierno y enviar comprobantes de vuelta a cada banco. 

Para que todo esto funcione en tiempo real sin congelarse, el código ha sido diseñado haciendo uso de programación asíncrona (`async/await`) en Python mediante la librería `asyncio`.

## ¿Cómo utiliza los `async`?

El uso del modelo asíncrono se concentra principalmente en **las operaciones de entrada/salida (I/O) a través de Internet** en los archivos `asfi/main.py` y `asfi/clients.py`:

1. **`async def fetch_bank_account(...)`**:
   Esta función realiza una petición HTTP (`GET`) a un banco individual utilizando la librería `httpx.AsyncClient`. Al usar `await client.get(...)`, el código de Python "pausa" esta función específica mientras espera que el banco responda, pero **no bloquea el resto del programa**.

2. **`await asyncio.gather(*tasks)`**:
   Esta es la pieza central de la magia asíncrona en `clients.py`. En lugar de llamar al Banco 1, esperar su respuesta, llamar al Banco 2, esperar su respuesta... el servicio crea 14 "tareas" (`tasks`) independientes y las ejecuta al mismo tiempo usando `asyncio.gather()`. Todos los bancos reciben la petición HTTP simultáneamente en el mismo segundo.

3. **`async def send_verification_code(...)` y `async def get_bcb_rate(...)`**:
   De forma similar, contactar al simulador del BCB y enviar los códigos POST de confirmación a los bancos está marcado como `async` para que el código pueda ceder el control del CPU a otras tareas mientras los paquetes de red viajan por el servidor.

---

## ¿Por qué es eficiente y por qué DEBE ser eficiente?

Si este código estuviera escrito de forma "síncrona" (tradicional y secuencial con la librería `requests` clásica), el tiempo total de ejecución sería igual a la **suma del tiempo de respuesta de todos los bancos**.

### 1. Tolerancia a la Latencia (El Problema del "Banco Lento")
Supongamos que 13 bancos responden en **0.1 segundos**, pero el servidor del Banco 14 está sufriendo tráfico y se tarda **5 segundos** en responder.
* **Modelo Síncrono Tradicional:** El hilo principal del programa se congelaría por 5 segundos esperando por ese único banco. El tiempo total para todo el proceso tomaría **5.0 + (13 * 0.1) = 6.3 segundos**.
* **Modelo Asíncrono Actual:** Las 14 peticiones se lanzan al mismo rato. Mientras el Banco 14 está calculando en sus 5 segundos, Python ya terminó de procesar a los 13 bancos anteriores en el fondo. El tiempo total es igual al *tiempo que tarda el banco más lento*, es decir, **5 segundos netos**. 

### 2. Ahorro de Recursos (CPU)
Tu procesador (CPU) es órdenes de magnitud más rápido que tu tarjeta de red y que el internet. Un programa tradicional que espera a la red mantiene todo el CPU "despierto" sin hacer nada (bloqueado). Con `asyncio`, cuando la red de Python dispara una petición a un banco, el sistema operativo le dice al CPU: *"Hey, no hagas nada, ve a hacer otros cálculos para la base de datos o encriptación, yo te aviso cuando vuelva el paquete de internet"*.

### 3. Evitar "Timeouts" en Cascada
El servicio ASFI actual se puede parametrizar para correr intervalos cada 30 segundos (con `python -m asfi.main --interval 30`). Si un proceso síncrono tardara más de 30 segundos en llamar a todos los bancos, el siguiente ciclo se encimaría con el anterior, creando un "cuello de botella" de peticiones encadenadas, sobrecargando el sistema hasta colapsar la memoria (Stack Overflow) o generar Timeouts en cadena. Gracias al paralelismo de concurrencia de I/O, el servicio de ASFI se liquida en cuestión de un par de segundos, sobrando tiempo para el siguiente ciclo de 30s.
