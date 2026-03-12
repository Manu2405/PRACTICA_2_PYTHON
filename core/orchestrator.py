import asyncio
import random
from typing import Dict, List

from .crypto_manager import decrypt_bank_payload
from .utils import generate_verification_hex, log_rate

BANKS = [
    {'id': 'bank_union', 'name': 'Banco Unión S.A.', 'users': 2247210},
    {'id': 'bank_mercantil', 'name': 'Banco Mercantil Santa Cruz S.A.', 'users': 1997520},
    {'id': 'bank_bnb', 'name': 'Banco Nacional de Bolivia S.A. (BNB)', 'users': 1498140},
    {'id': 'bank_bcp', 'name': 'Banco de Crédito de Bolivia S.A. (BCP)', 'users': 1398264},
    {'id': 'bank_bisa', 'name': 'Banco BISA S.A.', 'users': 1048698},
    {'id': 'bank_ganadero', 'name': 'Banco Ganadero S.A.', 'users': 948822},
    {'id': 'bank_economico', 'name': 'Banco Económico S.A.', 'users': 848946},
    {'id': 'bank_prodem', 'name': 'Banco Prodem S.A.', 'users': 749070},
    {'id': 'bank_solidario', 'name': 'Banco Solidario S.A.', 'users': 549318},
    {'id': 'bank_fortaleza', 'name': 'Banco Fortaleza S.A.', 'users': 349566},
    {'id': 'bank_fie', 'name': 'Banco FIE S.A.', 'users': 399504},
    {'id': 'bank_pyme', 'name': 'Banco PYME de la Comunidad S.A.', 'users': 224721},
    {'id': 'bank_desarrollo', 'name': 'Banco de Desarrollo Productivo S.A.M.', 'users': 99876},
    {'id': 'bank_argentina', 'name': 'Banco de la Nación Argentina', 'users': 19975},
]


def _compute_workers(users: int, base: int = 1) -> int:
    return max(base, int(users / 2000) + 1)


async def _process_bank_unit(bank: Dict, unit_no: int) -> Dict:
    rate = round(random.uniform(0.5, 4.0), 2)
    client_id = generate_verification_hex()

    log_rate(rate, client_id, bank['name'])

    # Simula un payload cifrado generado por el banco
    encrypted_payload = f"{bank['id']}-{unit_no}-{client_id}"
    decrypted = decrypt_bank_payload(bank['id'], encrypted_payload)

    # Simula latencia variable y carga
    await asyncio.sleep(random.uniform(0.05, 0.25))

    return {
        'bank': bank['name'],
        'bank_id': bank['id'],
        'worker': unit_no,
        'rate': rate,
        'decrypted': decrypted,
    }


async def run_orchestrator() -> List[Dict]:
    all_tasks = []

    for bank in BANKS:
        workers = _compute_workers(bank['users'])
        for worker_id in range(workers):
            all_tasks.append(_process_bank_unit(bank, worker_id + 1))

    # Se ejecutan los 14 bancos en paralelo, priorizando con más workers para mayor volumen
    results = await asyncio.gather(*all_tasks)
    return results


def start_orchestrator() -> List[Dict]:
    return asyncio.run(run_orchestrator())
