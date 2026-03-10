from pydantic import BaseModel\n\nclass Cuenta(BaseModel):\n    id: int\n    saldo_usd: float\n
