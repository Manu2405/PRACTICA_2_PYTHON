from fastapi import FastAPI, Response
from .exchange import format_rate, get_rate, start_simulator

app = FastAPI(title="BCB Exchange Simulator")


@app.on_event("startup")
def startup():
    start_simulator()


@app.get("/rate")
def get_rate_endpoint(response: Response):
    rate = get_rate()
    response.headers["Cache-Control"] = "no-store"

    return {
        "currency": "USD/BOB",
        "rate": format_rate(rate)
    }