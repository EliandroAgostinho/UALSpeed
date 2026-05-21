from fastapi import APIRouter, HTTPException
from models import Piloto, PilotoResponse
from database import pilotos_collection
from bson import ObjectId

router = APIRouter()

@router.post("/pilotos", response_model=PilotoResponse, status_code=201)
async def criar_piloto(piloto: Piloto):
    existente = await pilotos_collection.find_one({"numero": piloto.numero})
    if existente:
        raise HTTPException(status_code=409, detail="Piloto já existe")

    result = await pilotos_collection.insert_one(piloto.model_dump())
    criado = await pilotos_collection.find_one({"_id": result.inserted_id})
    criado["id"] = str(criado["_id"])
    return PilotoResponse(**criado)

@router.get("/pilotos")
async def listar_pilotos():
    pilotos = []
    async for p in pilotos_collection.find():
        p["id"] = str(p["_id"])
        del p["_id"]
        pilotos.append(p)
    return {"total": len(pilotos), "pilotos": pilotos}