from pydantic import BaseModel\n\nclass Transaction(BaseModel):\n    id: int\n    detalle: str\n
