"""Start 14 bank API simulators in parallel.

Each simulated API is a FastAPI service that validates a Bearer token and
returns a deterministic verification code for the provided account data.

This script is meant to be run from the workspace root:

    python -m api.run_all

"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# Ensure we run from the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.insert(0, project_root)


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


def _build_command(bank: str, port: int) -> list[str]:
    env_file = os.path.join(os.path.dirname(__file__), "envs", f"{bank}.env")
    return [
        sys.executable,
        "-m",
        "api.main",
        "--bank-id",
        bank,
        "--port",
        str(port),
        "--env-file",
        env_file,
    ]


def _run_bank_server(bank: str, port: int) -> subprocess.Popen:
    cmd = _build_command(bank, port)
    print(f"Starting {bank} on http://127.0.0.1:{port} ...")
    # Start in a new process so we can start all banks in parallel.
    return subprocess.Popen(cmd)


def main():
    # Ports: 8881..8894 (one per bank)
    start_port = 8881

    processes = []
    for i, bank in enumerate(BANKS):
        port = start_port + i
        proc = _run_bank_server(bank, port)
        processes.append((bank, proc))

    try:
        # Keep the main process alive while the child servers run.
        print("All bank APIs started. Press Ctrl+C to stop.")
        for proc in processes:
            proc[1].wait()
    except KeyboardInterrupt:
        print("Stopping all bank API processes...")
        for _, proc in processes:
            proc.terminate()



if __name__ == "__main__":
    main()
