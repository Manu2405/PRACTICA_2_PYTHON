import random
import time
import threading
from .config import BASE_RATE, INTERVAL

current_rate = BASE_RATE


def _compute_rate() -> float:
    """Compute a new exchange rate around the base rate."""
    variation = random.uniform(-0.9999, 0.9999)
    return round(BASE_RATE + variation, 4)


def update_rate():
    global current_rate

    while True:
        current_rate = _compute_rate()
        print("Nuevo tipo de cambio:", current_rate)  # para ver cambios
        time.sleep(INTERVAL)


def start_simulator():
    thread = threading.Thread(target=update_rate)
    thread.daemon = True
    thread.start()


def get_rate() -> float:
    """Return current rate without modifying it."""
    return current_rate


def format_rate(rate: float) -> str:
    return f"{rate:.4f}"