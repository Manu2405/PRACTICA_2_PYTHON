"""Query exactly 1 account from all 14 bank API endpoints and print the result.

Run this after starting the APIs (e.g., `python -m api.run_all`).
"""

import json
import urllib.request

BANKS = [
    "banco_union",
    "bcp",
    "fortaleza",
    "mercantil",
    "bisa",
    "solidario",
    "desarrollo_productivo",
    "bnb",
    "economico",
    "fie",
    "ganadero",
    "prodem",
    "pyme_comunidad",
    "argentina",
]

TOKENS = {
    "banco_union": "token_banco_union",
    "bcp": "token_bcp",
    "fortaleza": "token_fortaleza",
    "mercantil": "token_mercantil",
    "bisa": "token_bisa",
    "solidario": "token_solidario",
    "desarrollo_productivo": "token_desarrollo_productivo",
    "bnb": "token_bnb",
    "economico": "token_economico",
    "fie": "token_fie",
    "ganadero": "token_ganadero",
    "prodem": "token_prodem",
    "pyme_comunidad": "token_pyme_comunidad",
    "argentina": "token_argentina",
}


def fetch(url: str, token: str):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def main():
    print("Fetching 1 account from each of the 14 bank APIs...")
    print("-" * 60)

    for i, bank in enumerate(BANKS):
        port = 8881 + i
        url = f"http://127.0.0.1:{port}/accounts?limit=1"
        token = TOKENS[bank]
        try:
            data = fetch(url, token)
            accounts = data.get("accounts", [])
            if accounts:
                account = accounts[0]
                print(f"BANK: {bank} (Port {port})")
                print(f"Cuenta: {json.dumps(account, indent=2)}")
            else:
                print(f"BANK: {bank} (Port {port}) - NO ACCOUNTS FOUND")
        except Exception as e:
            print(f"BANK: {bank} (Port {port}) - ERROR: {e}")
        print("-" * 60)


if __name__ == "__main__":
    main()
