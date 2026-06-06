import redis
import json
import asyncio
import logging
import threading
from datetime import datetime
from database import resultados_collection, classificacao_collection
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger(__name__)

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://mongo-primary:27017,mongo-secondary1:27017,mongo-secondary2:27017/?replicaSet=ualspped-rs"
)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)


async def processar_telemetria(dados: dict, db):
    """
    Recebe os dados e o cliente MongoDB dedicado desta thread.
    Usa o db passado como argumento — não o da aplicação principal.
    """
    try:
        carro = dados['carro_numero']
       # piloto = dados['piloto_nome']
        volta = dados['volta_atual']
        velocidade = dados['velocidade']
        rpm = dados['rpm']
        posicao = dados['posicao_pista']
        timestamp = datetime.fromisoformat(dados['timestamp'])
        
        # Vai buscar o nome oficial do piloto registado
        piloto_registado = await db["pilotos"].find_one({"numero": carro})
        if piloto_registado:
            piloto_nome = piloto_registado["nome"]
            equipa = piloto_registado.get("equipa", "")
        else:
            piloto_nome = dados.get('piloto_nome', f'Carro {carro}')
            equipa = ""

        # Guarda resultado da volta
        await db["resultados"].update_one(
            {"carro_numero": carro, "volta": volta},
            {
                "$set": {
                    "piloto_nome": piloto_nome,
                    "equipa": equipa,
                    "posicao": posicao,
                    "timestamp": timestamp
                },
                "$max": {"velocidade_max": velocidade},
                "$min": {"velocidade_min": velocidade},
                "$inc": {
                    "total_leituras": 1,
                    "soma_rpm": rpm
                }
            },
            upsert=True
        )

        # Actualiza classificação em tempo real
        await db["classificacao"].update_one(
            {"carro_numero": carro},
            {"$set": {
                "piloto_nome": piloto_nome,
                "equipa": equipa,
                "posicao": posicao,
                "voltas_completas": volta,
                "ultima_velocidade": velocidade,
                "ultima_atualizacao": timestamp
            }},
            upsert=True
        )

        logger.info(f" Processado:{piloto_nome} | Carro {carro} | Pos {posicao} | {velocidade} km/h")

    except Exception as e:
        logger.error(f" Erro ao processar telemetria: {e}", exc_info=True)


def iniciar_consumer():
    """
    Cria uma thread dedicada com o seu próprio event loop
    E o seu próprio cliente MongoDB — evita conflito de loops.
    """

    def consumer_loop():
        # Event loop dedicado para esta thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Cliente MongoDB DEDICADO a esta thread
        # Criado DENTRO da thread para usar o loop correcto
        client = AsyncIOMotorClient(MONGO_URL, io_loop=loop)
        db = client["ualspped"]

        logger.info(" Consumer Redis iniciado — à escuta no canal 'telemetria'")

        try:
            pubsub = redis_client.pubsub()
            pubsub.subscribe('telemetria')
            logger.info(" Subscrito ao canal 'telemetria' com sucesso")

            for mensagem in pubsub.listen():
                if mensagem['type'] == 'message':
                    try:
                        dados = json.loads(mensagem['data'])
                        logger.info(f"📨 Mensagem recebida: Carro {dados.get('carro_numero')}")
                        # Passa o db dedicado para a função
                        loop.run_until_complete(processar_telemetria(dados, db))
                    except json.JSONDecodeError as e:
                        logger.error(f"Erro JSON: {e}")
                    except Exception as e:
                        logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro no consumer loop: {e}", exc_info=True)
        finally:
            client.close()
            loop.close()

    thread = threading.Thread(target=consumer_loop, daemon=True)
    thread.start()
    logger.info(" Thread do consumer iniciada")