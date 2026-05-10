from fastapi import APIRouter, HTTPException
from models import TelemetriaInput, TelemetriaResponse
from datetime import datetime
import redis
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Ligação ao Redis
redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)

@router.post("/telemetria", response_model=TelemetriaResponse)
async def receber_telemetria(dados: TelemetriaInput):
    """
    Recebe dados de telemetria de um carro de F1
    e publica na fila Redis para processamento.
    """
    try:
        # Adiciona timestamp se não vier preenchido
        if not dados.timestamp:
            dados.timestamp = datetime.utcnow()

        # Converte para dicionário para publicar no Redis
        payload = dados.model_dump()
        payload['timestamp'] = payload['timestamp'].isoformat()

        # Publica no canal Redis 'telemetria'
        redis_client.publish('telemetria', json.dumps(payload))

        # Guarda também no histórico (lista Redis)
        redis_client.lpush('historico_telemetria', json.dumps(payload))
        redis_client.ltrim('historico_telemetria', 0, 999)  # Guarda os últimos 1000

        logger.info(f"Telemetria recebida: Carro {dados.carro_numero} a {dados.velocidade} km/h")

        return TelemetriaResponse(
            status="ok",
            mensagem="Telemetria recebida e publicada na fila",
            dados_recebidos=dados
        )

    except redis.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Serviço Redis indisponível"
        )

@router.get("/telemetria/historico")
async def get_historico(limite: int = 10):
    """
    Retorna os últimos registos de telemetria.
    """
    try:
        historico = redis_client.lrange('historico_telemetria', 0, limite - 1)
        return {
            "total": len(historico),
            "dados": [json.loads(item) for item in historico]
        }
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Serviço Redis indisponível")

@router.get("/telemetria/status")
async def status():
    """
    Verifica se o serviço e o Redis estão operacionais.
    """
    try:
        redis_client.ping()
        return {"status": "online", "redis": "conectado"}
    except redis.ConnectionError:
        return {"status": "online", "redis": "desconectado"}