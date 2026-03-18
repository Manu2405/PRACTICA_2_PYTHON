import re

with open("generated_keys.txt") as f:
    text = f.read()

rsa_priv = text.split("RSA_PRIV\n")[1].split("ECC_PRIV\n")[0].strip()
ecc_priv = text.split("ECC_PRIV\n")[1].strip()

from Crypto.PublicKey import RSA, ECC
rsa_key = RSA.import_key(rsa_priv)
rsa_pub = rsa_key.publickey().export_key().decode()

ecc_key = ECC.import_key(ecc_priv)
ecc_pub = ecc_key.public_key().export_key(format="PEM")

# Write to keys.py
with open("services/crypto/keys.py", "r") as f:
    keys_text = f.read()

keys_text = re.sub(r'RSA_PUBLIC_KEY\s*=\s*\"\"\"[\s\S]*?\"\"\"', f'RSA_PUBLIC_KEY = """{rsa_pub}"""', keys_text)
keys_text = re.sub(r'ECC_PUBLIC_KEY\s*=\s*\"\"\"[\s\S]*?\"\"\"', f'ECC_PUBLIC_KEY = """{ecc_pub}"""', keys_text)

with open("services/crypto/keys.py", "w") as f:
    f.write(keys_text)
    
print("Updated services/crypto/keys.py!")

# Write to .env
with open("asfi/envs/.env", "r") as f:
    env_text = f.read()

# Replace empty keys with multiline syntax
env_text = re.sub(r'RSA_PRIVATE_KEY=""', f'RSA_PRIVATE_KEY="{rsa_priv}"', env_text)
env_text = re.sub(r'ECC_PRIVATE_KEY=""', f'ECC_PRIVATE_KEY="{ecc_priv}"', env_text)

with open("asfi/envs/.env", "w") as f:
    f.write(env_text)

print("Updated asfi/envs/.env!")

