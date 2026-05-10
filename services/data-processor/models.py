from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TelemetriaInput(BaseModel):
    carro_numero: int = Field(..., ge=1, le=99, description="Número do carro")
    piloto_nome: str = Field(..., min_length=2)
    velocidade: float = Field(..., ge=0, le=400, description="Velocidade em km/h")
    rpm: int = Field(..., ge=0, le=15000)
    posicao_pista: int = Field(..., ge=1, le=20, description="Posição na corrida")
    volta_atual: int = Field(..., ge=1)
    timestamp: Optional[datetime] = None 

class TelemetriaResponse(BaseModel):
    status: str
    mensagem: str
    dados_recebidos: TelemetriaInput 
    
