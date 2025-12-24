from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer,Float,JSON
from sqlalchemy.sql import func
from db.base import Base
import uuid


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # user | assistant 
    content = Column(Text)
    tokens_used = Column(Integer, nullable=True)
    message_cost = Column(Float, nullable=True)
    sequence_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, nullable=True)
