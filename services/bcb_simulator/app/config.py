import os

BASE_RATE = float(os.getenv("BASE_RATE", 6.96))
INTERVAL = int(os.getenv("INTERVAL", 3))
PORT = int(os.getenv("PORT", 8001))