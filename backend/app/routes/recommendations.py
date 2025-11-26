from fastapi import APIRouter
from app.services.rag_service import get_recommendations

router = APIRouter()

@router.get("/recommendations")
async def recommendations():
return await get_recommendations()