from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128))
    user_phone = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    role = Column(String(32), index=True)  # user | assistant | system
    content = Column(Text)
    external_id = Column(String(128), index=True, nullable=True)   # <── AÑADIR ESTO
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation = relationship("Conversation", back_populates="messages")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    phone = Column(String(32), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    chat_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    channel = Column(String(32), index=True, nullable=True)
    last_message = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    total_messages = Column(Integer, default=0)