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
@router.put("/update_profile/{phone}")
def update_profile(phone: str, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        return {"error": "User not found"}

    for k, v in data.items():
        setattr(user, k, v)

    # Calcular si ya completó todo
    user.profile_completed = bool(user.name and user.email and user.address)

    db.commit()
    db.refresh(user)
    return user


# Eliminar usuario
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return {"error": "User not found"}

    db.delete(u)
    db.commit()
    return {"status": "deleted"}
