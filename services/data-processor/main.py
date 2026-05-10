from fastapi import FastAPI
from routes.telemetria import router as telemetria_router
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="UALSpeed - Data Processor",
    description="Serviço de processamento de telemetria de F1",
    version="1.0.0"
)

# Equivalente ao register_blueprint do Flask
app.include_router(
    telemetria_router,
    prefix="/api/v1",
    tags=["Telemetria"]
)

@app.get("/")
async def root():
    return {
        "servico": "data-processor",
        "versao": "1.0.0",
        "descricao": "UALSpeed - Sistema distribuído de dados de F1"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}