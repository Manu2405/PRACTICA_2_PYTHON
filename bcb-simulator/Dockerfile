FROM python:3.11-slim

WORKDIR /app

# Usamos versiones compatibles con BaseSettings de pydantic v1
RUN pip install --no-cache-dir fastapi==0.103.2 uvicorn[standard]==0.23.2 pydantic==1.10.13

COPY ./config.py ./config.py
COPY ./main.py ./main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

