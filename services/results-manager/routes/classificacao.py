from fastapi import APIRouter
from database import classificacao_collection, resultados_collection

router = APIRouter()

@router.get("/classificacao")
async def get_classificacao():
    """Classificação actual da corrida em tempo real."""
    classificacao = []
    async for item in classificacao_collection.find().sort("posicao", 1):
        item["id"] = str(item["_id"])
        del item["_id"]
        if "ultima_atualizacao" in item:
            item["ultima_atualizacao"] = item["ultima_atualizacao"].isoformat()
        classificacao.append(item)
    return {"total": len(classificacao), "classificacao": classificacao}



@router.get("/resultados/{carro_numero}")
async def get_resultados_carro(carro_numero: int):
    """Histórico de voltas de um carro específico."""
    resultados = []
    async for r in resultados_collection.find(
        {"carro_numero": carro_numero}
    ).sort("volta", 1):
        r["id"] = str(r["_id"])
        del r["_id"]
        # Calcula rpm_medio aqui
        if r.get("total_leituras", 0) > 0:
            r["rpm_medio"] = round(r["soma_rpm"] / r["total_leituras"])
        if "timestamp" in r:
            r["timestamp"] = r["timestamp"].isoformat()
        resultados.append(r)

    if not resultados:
        return {"mensagem": f"Sem dados para o carro {carro_numero}"}
    return {
        "carro": carro_numero,
        "total_voltas": len(resultados),
        "voltas": resultados
    }