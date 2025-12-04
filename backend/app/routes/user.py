from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.models.db_models import User

router = APIRouter()

# obtener todos los usuarios
@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Obtener un usuario por id
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()


# Crear usuario desde el frontend o el backend
@router.post("/")
def create_user(user: dict, db: Session = Depends(get_db)):
    u = User(**user)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

# Editar usuario
@router.put("/{user_id}")
def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return {"error": "User not found"}

    for k, v in user_data.items():
        setattr(u, k, v)

    db.commit()
    db.refresh(u)
    return u

# Eliminar usuario
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return {"error": "User not found"}

    db.delete(u)
    db.commit()
    return {"status": "deleted"}
