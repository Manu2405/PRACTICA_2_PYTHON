from asfi.config import BANKS
from asfi.db import get_bank_algorithm
for b in BANKS:
    print(f"{b['id']:2} {b['name']:25}: {get_bank_algorithm(b['id'])}")
