from api.db import fetch_accounts
import json

def main():
    print("Testing Argentina accounts fetch...")
    res = fetch_accounts("argentina", limit=1, offset=0)
    print("Result:", json.dumps(res, indent=2))

if __name__ == '__main__':
    main()
