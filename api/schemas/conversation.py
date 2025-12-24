from pydantic import BaseModel
from typing import List
from datetime import datetime
from enum import Enum


class ConversationMode(str, Enum):
    OPEN_CHAT = "OPEN_CHAT"
    DOCUMENT_QA = "DOCUMENT_QA"
    DOCUMENT_SUMMARY = "DOCUMENT_SUMMARY"


class CreateConversationRequest(BaseModel):
    conversation_mode: ConversationMode
    title: str


class ConversationResponse(BaseModel):
    id: str
    conversation_mode: ConversationMode
    created_at: datetime
    title: str


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
