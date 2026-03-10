from pydantic import BaseSettings\n\nclass Settings(BaseSettings):\n    PRECISION_DECIMALES: int = 2\n\nsettings = Settings()\n
