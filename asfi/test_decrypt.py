#!/usr/bin/env python3
"""Test script to fetch one account from each bank API and decrypt all fields."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import asfi modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from asfi.clients import fetch_all_banks_accounts
from asfi.config import BANKS
from asfi.crypto_router import decrypt_account_fields, decrypt_by_algorithm
from asfi.db import get_bank_algorithm, normalize_account_dict


async def test_decrypt_accounts():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    bank_names = [b["name"] for b in BANKS]
    
    print("\n" + "=" * 100)
    print("FETCHING AND DECRYPTING ACCOUNTS FROM ALL BANKS")
    print("=" * 100)
    
    accounts_by_bank = await fetch_all_banks_accounts(bank_names, limit=1)

    for bank_cfg in BANKS:
        bank_name = bank_cfg["name"]
        bank_id = bank_cfg["id"]
        raw_account = accounts_by_bank.get(bank_name)

        if not raw_account:
            print(f"\n❌ Bank: {bank_name:30s} (ID: {bank_id:2d}) - NO DATA RETURNED")
            continue

        # Normalize the account data
        account = normalize_account_dict(raw_account)

        algorithm = get_bank_algorithm(bank_id) or ""
        decrypted = decrypt_account_fields(account, algorithm)

        print(f"\n{'='*100}")
        print(f"Bank: {bank_name:30s} (ID: {bank_id:2d})")
        print(f"Algorithm: {algorithm}")
        print(f"{'-'*100}")
        
        # Show encrypted fields
        print("ENCRYPTED DATA (from API):")
        print(f"  Nro:             {account.get('Nro')}")
        print(f"  Identificacion:  {str(account.get('Identificacion'))}")
        print(f"  Nombres:         {str(account.get('Nombres'))}")
        print(f"  Apellidos:       {str(account.get('Apellidos'))}")
        print(f"  NroCuenta:       {str(account.get('NroCuenta'))}")
        print(f"  Saldo/SaldoUSD:  {str(account.get('Saldo') or account.get('SaldoUSD'))}")
        
        print("\nDECRYPTED DATA:")
        print(f"  Nro:             {decrypted.get('Nro')}")
        print(f"  Identificacion:  {decrypted.get('Identificacion')}")
        print(f"  Nombres:         {decrypted.get('Nombres')}")
        print(f"  Apellidos:       {decrypted.get('Apellidos')}")
        print(f"  NroCuenta:       {decrypted.get('NroCuenta')}")
        
        # Balance decryption
        saldo_key = 'Saldo' if account.get('Saldo') else ('SaldoUSD' if account.get('SaldoUSD') else 'SaldoBs')
        saldo_encrypted = account.get(saldo_key)
        saldo_decrypted = decrypted.get(saldo_key)
        
        if saldo_encrypted and saldo_decrypted:
            print(f"  {saldo_key} (encrypted): {str(saldo_encrypted)}")
            print(f"  {saldo_key} (decrypted): {saldo_decrypted}")
            print(f"  ✓ Balance decryption successful!")
        else:
            print(f"  {saldo_key}: {decrypted.get(saldo_key)}")


if __name__ == "__main__":
    asyncio.run(test_decrypt_accounts())