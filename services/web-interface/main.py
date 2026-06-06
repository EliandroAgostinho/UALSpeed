from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import os
import logging
from datetime import datetime
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="UALSpeed", version="1.0.0")
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

DATA_PROCESSOR_URL = os.getenv("DATA_PROCESSOR_URL", "http://data-processor:8000")
RESULTS_MANAGER_URL = os.getenv("RESULTS_MANAGER_URL", "http://results-manager:8001")

# ─────────────────────────────────────────
# PÁGINAS HTML
# ─────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("/app/static/index.html") as f:
        return f.read()

@app.get("/corrida", response_class=HTMLResponse)
async def corrida():
    with open("/app/static/corrida.html") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    with open("/app/static/admin.html") as f:
        return f.read()

# ─────────────────────────────────────────
# APIs PARA O DASHBOARD
# ─────────────────────────────────────────

@app.get("/api/metricas")
async def get_metricas():
    async with httpx.AsyncClient(timeout=5.0) as client:
        servicos = {}
        for nome, url in [
            ("data-processor", DATA_PROCESSOR_URL),
            ("results-manager", RESULTS_MANAGER_URL)
        ]:
            try:
                r = await client.get(f"{url}/health")
                servicos[nome] = {
                    "status": "online" if r.status_code == 200 else "degradado",
                    "codigo": r.status_code
                }
            except Exception:
                servicos[nome] = {"status": "offline", "codigo": 0}

        total_eventos = 0
        ultimo_evento = None
        try:
            r = await client.get(
                f"{DATA_PROCESSOR_URL}/api/v1/telemetria/historico?limite=1"
            )
            if r.status_code == 200:
                dados = r.json()
                total_eventos = dados.get("total", 0)
                if dados.get("dados"):
                    ultimo_evento = dados["dados"][0]
        except Exception:
            pass

        classificacao = []
        try:
            r = await client.get(f"{RESULTS_MANAGER_URL}/api/v1/classificacao")
            if r.status_code == 200:
                classificacao = r.json().get("classificacao", [])
        except Exception:
            pass

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "servicos": servicos,
            "total_eventos": total_eventos,
            "ultimo_evento": ultimo_evento,
            "classificacao": classificacao,
            "cluster": {
                "nos_activos": 1,
                "replicas_data_processor": 2,
                "replicas_results_manager": 2
            }
        }

# ─────────────────────────────────────────
# APIs PARA A CORRIDA
# ─────────────────────────────────────────

@app.get("/api/corrida/classificacao")
async def get_classificacao_corrida():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(f"{RESULTS_MANAGER_URL}/api/v1/classificacao")
            return r.json()
        except Exception:
            return {"classificacao": [], "total": 0}

@app.get("/api/corrida/telemetria")
async def get_telemetria_recente():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(
                f"{DATA_PROCESSOR_URL}/api/v1/telemetria/historico?limite=5"
            )
            return r.json()
        except Exception:
            return {"dados": [], "total": 0}

# ─────────────────────────────────────────
# APIs PARA O ADMIN
# ─────────────────────────────────────────

@app.get("/api/admin/pilotos")
async def listar_pilotos():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(f"{RESULTS_MANAGER_URL}/api/v1/pilotos")
            return r.json()
        except Exception:
            return {"pilotos": [], "total": 0}

@app.post("/api/admin/pilotos")
async def criar_piloto(request: Request):
    dados = await request.json()
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.post(
                f"{RESULTS_MANAGER_URL}/api/v1/pilotos",
                json=dados
            )
            return r.json()
        except Exception as e:
            return {"erro": str(e)}

@app.post("/api/corrida/telemetria")
async def enviar_telemetria(request: Request):
    dados = await request.json()
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.post(
                f"{DATA_PROCESSOR_URL}/api/v1/telemetria",
                json=dados
            )
            return r.json()
        except Exception as e:
            return {"erro": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/admin/pilotos/{numero}/iniciar-corrida")
async def iniciar_corrida_piloto(numero: int, request: Request):
    """
    Coloca um piloto registado na corrida
    enviando o primeiro evento de telemetria.
    """
    dados_extra = await request.json()
    posicao = dados_extra.get("posicao", 1)
    volta = dados_extra.get("volta", 1)

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Vai buscar o piloto registado
        try:
            r = await client.get(f"{RESULTS_MANAGER_URL}/api/v1/pilotos/{numero}")
            if r.status_code == 404:
                return {"erro": "Piloto não encontrado"}
            piloto = r.json()
        except Exception:
            return {"erro": "Erro ao buscar piloto"}

        # Envia telemetria inicial
        telemetria = {
            "carro_numero": piloto["numero"],
            "piloto_nome": piloto["nome"],
            "velocidade": 0.0,
            "rpm": 0,
            "posicao_pista": posicao,
            "volta_atual": volta
        }

        try:
            r = await client.post(
                f"{DATA_PROCESSOR_URL}/api/v1/telemetria",
                json=telemetria
            )
            return {
                "status": "ok",
                "mensagem": f"{piloto['nome']} adicionado à corrida na posição {posicao}",
                "piloto": piloto
            }
        except Exception:
            return {"erro": "Erro ao enviar telemetria"}