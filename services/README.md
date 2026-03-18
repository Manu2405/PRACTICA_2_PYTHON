# Services Module

Contiene servicios de **encriptación** para saldos.

## Submódulos

- `crypto/`: Algoritmos criptográficos.
  - `classical.py`: Caesar, Atbash, Vigenère, Playfair, Hill.
  - `symmetric.py`: DES, 3DES, Blowfish, AES, ChaCha20.
  - `asymmetric.py`: RSA, ElGamal, ECC.
  - `keys.py`: Gestión de claves (desde env vars).
  - `utils.py`: Utilidades cripto.

- `bcb_simulator/`: Simulador del Banco Central de Bolivia (no usado en ETL/APIs).

## Uso
Importar desde `crypto_router.py` para encriptar saldos por banco.</content>
<parameter name="filePath">/home/lcoin/Desktop/GIt/SD-Practica2/PRACTICA2/services/README.md