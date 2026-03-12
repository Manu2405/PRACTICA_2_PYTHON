from fastapi import FastAPI
from core.orchestrator import run_orchestrator

app = FastAPI(title='Orquestador 14 Bancos', version='1.0')


@app.get('/orchestrator/status')
async def status():
    return {'status': 'ok', 'banks': 14}


@app.post('/orchestrator/run')
async def run():
    results = await run_orchestrator()
    return {'processed': len(results), 'detail': results}
