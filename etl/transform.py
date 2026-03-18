from etl.crypto_router import encrypt_by_bank

def transform_row(row):

    new_row = dict(row)

    bank_id = int(new_row["IdBanco"])

    saldo = float(new_row["Saldo"])
    saldo = f"{saldo:.4f}"

    saldo_cifrado = encrypt_by_bank(bank_id, saldo)

    new_row["Saldo"] = saldo_cifrado

    return new_row