from sqlalchemy.orm import Session
from app.models.db_models import User
# import de regular expressions para validaciones
import re

class UserService:
    @staticmethod
    def validate_email(email: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        return bool(re.match(r"^\+?\d{7,15}$", phone))
    @staticmethod
    def update_profile(db: Session, phone: str, data: dict):
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            return None

        # Validar email
        if "email" in data:
            if not UserService.validate_email(data["email"]):
                raise ValueError("invalid_email")

        # Validar dirección
        if "address" in data and len(data["address"]) < 5:
            raise ValueError("invalid_address")

        # Aplicar cambios seguros
        for k, v in data.items():
            setattr(user, k, v)

        user.profile_completed = bool(
            user.name and user.email and user.address
        )

        db.commit()
        db.refresh(user)
        return user