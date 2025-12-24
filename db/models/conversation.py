from sqlalchemy import Column, String, DateTime, Enum,ARRAY,JSON,ForeignKey
from sqlalchemy.sql import func
from db.base import Base
import enum
import uuid
from db.models.user import User


class ConversationMode(str, enum.Enum):
    OPEN_CHAT = "OPEN_CHAT"
    DOCUMENT_QA = "DOCUMENT_QA"
    DOCUMENT_SUMMARY = "DOCUMENT_SUMMARY"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    conversation_mode = Column(Enum(ConversationMode), nullable=False)
    conversation_summary = Column(String, nullable=True)
    models_used = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    meta_data = Column(JSON, nullable=True)
