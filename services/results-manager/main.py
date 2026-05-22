from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.pilotos import router as pilotos_router
from routes.classificacao import router as classificacao_router
from database import init_db
from consumer import iniciar_consumer
import logging
import socket

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa ao arrancar
    await init_db()
    iniciar_consumer()
    yield
    # Executa ao desligar (se necessário)

app = FastAPI(
    title="UALSpeed - Results Manager",
    description="Serviço de gestão de classificações e resultados de F1",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(pilotos_router, prefix="/api/v1", tags=["Pilotos"])
app.include_router(classificacao_router, prefix="/api/v1", tags=["Classificação"])

@app.get("/")
async def root():
    return {"servico": "results-manager", "versao": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/instancia")
async def instancia():
    return {
        "hostname": socket.gethostname(),
        "servico": "results-manager"
    }