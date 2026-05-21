from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://mongo-primary:27017,mongo-secondary1:27017,mongo-secondary2:27017/?replicaSet=ualspped-rs"
)
DB_NAME = "ualspped"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

pilotos_collection = db["pilotos"]
resultados_collection = db["resultados"]
classificacao_collection = db["classificacao"]

async def init_db():
    """Aguarda o MongoDB estar pronto e cria índices."""
    max_tentativas = 10
    for tentativa in range(max_tentativas):
        try:
            # Testa a ligação antes de criar índices
            await client.admin.command('ping')
            logger.info(" MongoDB ligado com sucesso!")

            await pilotos_collection.create_index("numero", unique=True)
            await resultados_collection.create_index(
                [("carro_numero", 1), ("volta", 1)]
            )
            await classificacao_collection.create_index(
                "carro_numero", unique=True
            )
            logger.info(" MongoDB Replica Set inicializado com índices")
            return

        except Exception as e:
            logger.warning(f" MongoDB não disponível (tentativa {tentativa+1}/{max_tentativas}): {e}")
            await asyncio.sleep(5)

    raise Exception(" MongoDB não ficou disponível após várias tentativas")