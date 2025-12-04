from fastapi import APIRouter
from app.services.recomendation_service import get_recommendations

router = APIRouter()

@router.get("/")
async def recommendations():
    return await get_recommendations()