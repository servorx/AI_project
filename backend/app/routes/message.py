from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.models.db_models import Conversation, Message, User
from typing import List
# import run_ingest from app.scripts.ingest_kb
from app.scripts.ingest_kb import ingest

router = APIRouter()

# obtener todos los mensajes
@router.get("/")
def list_messages(
    conversation_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    q = db.query(Message)
    if conversation_id:
        q = q.filter(Message.conversation_id == conversation_id)
    total = q.count()
    items = q.order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [{"id": m.id, "conversation_id": m.conversation_id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in items]}

# ➤ Editar un mensaje
@router.put("/{msg_id}")
def edit_message(msg_id: int, data: dict, db: Session = Depends(get_db)):
    m = db.query(Message).filter(Message.id == msg_id).first()
    if not m:
        return {"error": "Message not found"}

    if "content" in data:
        m.content = data["content"]

    db.commit()
    db.refresh(m)
    return m


# ➤ Eliminar un mensaje
@router.delete("/{msg_id}")
def delete_message(msg_id: int, db: Session = Depends(get_db)):
    m = db.query(Message).filter(Message.id == msg_id).first()

    if not m:
        return {"error": "Message not found"}

    db.delete(m)
    db.commit()
    return {"status": "deleted"}