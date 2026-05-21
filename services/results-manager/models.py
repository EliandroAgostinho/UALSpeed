from pydantic import BaseModel, Field
from typing import Optional 
from datetime import datetime

class Piloto(BaseModel):
    numero: int = Field(..., ge=1, le=99)
    nome: str = Field(..., min_length=2)
    equipa: str
    nacionalidade: str
    pontos: float = 0.0
    

class PilotoResponse(Piloto):
    id : Optional[str] = None
    
class ResultadoVolta(BaseModel):
    carro_numero: int
    piloto_nome: str
    volta: int
    tempo_volta: Optional[float] = None
    posicao: int
    velocidade_max: float
    rpm_medio: int
    timestamp: datetime
    
class ClassificacaoItem(BaseModel):
    posicao: int
    carro_numero: int
    piloto_nome: str
    voltas_completas: int
    ultima_velocidade: float
    ultima_atualizacao: datetime
