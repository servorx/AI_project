from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.models.db_models import Conversation, Message, User
from typing import List
# import run_ingest from app.scripts.ingest_kb
from app.scripts.ingest_kb import ingest

router = APIRouter()

@router.get("/conversations")
def list_conversations(
    phone: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    q = db.query(Conversation)
    if phone:
        q = q.filter(Conversation.user_phone == phone)
    total = q.count()
    items = q.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [{"id": c.id, "session_id": c.session_id, "user_phone": c.user_phone, "created_at": c.created_at} for c in items]}

# este endpoint en especifico es para recargar la ingesta de KB de forma manual en caso de que se deba de actualizar con el nuevo KB o un nuevo documento
@router.post("/reload-kb")
async def reload_kb():
    log_text = await ingest()
    return {"status": "ok", "detail": log_text}
