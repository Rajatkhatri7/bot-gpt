from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func ,delete



from db.session import get_db
from services.llm.factory import get_llm_client
from core.config import settings
from sqlalchemy import select

from db.models.conversation import Conversation
from db.models.message import Message
from db.models.user import User



from api.schemas.conversation import (
    CreateConversationRequest,
    ConversationResponse
)
import json
from utils.auth_helper import verify_user
from services.rag.rag_service import RAGService
from api.schemas.conversation import ConversationMode
from db.models.document import Document




router = APIRouter()




@router.post("", response_model=ConversationResponse)
async def create_conversation(
    payload: CreateConversationRequest,
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = Conversation(
        user_id=user.id,  
        conversation_mode=payload.conversation_mode,
        title=payload.title
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    payload: CreateConversationRequest,
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = Conversation(
        user_id=user.id,  # Use authenticated user's ID
        conversation_mode=payload.conversation_mode,
        title=payload.title
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.get("")
async def list_conversations(
    page: int = 1,
    limit: int = 10,
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == user.id)
    )
    total_conversations = total_result.scalar()
    
    offset = (page - 1) * limit
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    conversations = result.scalars().all()
    
    return {
        "conversations": [
            ConversationResponse(
                id=c.id,
                conversation_mode=c.conversation_mode,
                created_at=c.created_at,
                title=c.title
            ) for c in conversations
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_conversations": total_conversations,
            "total_pages": (total_conversations + limit - 1) // limit
        }
    }


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    page: int = 1,
    limit: int = 10,
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conv = conv.scalar_one_or_none()
    
    if not conv:
        return {"error": "Conversation not found"}
    
    # total message count
    total_result = await db.execute(
        select(func.count(Message.id))
        .where(Message.conversation_id == conversation_id)
    )
    total_messages = total_result.scalar()
    
    # paginated messages (most recent first)
    offset = (page - 1) * limit
    result = await db.execute(
        select(Message.role, Message.content, Message.created_at, Message.sequence_number)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.sequence_number.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.all()
    
    return {
        "conversation_id": conv.id,
        "mode": conv.conversation_mode,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in reversed(messages)  
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_messages": total_messages,
            "total_pages": (total_messages + limit - 1) // limit
        }
    }

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        return {"error": "Conversation not found"}
    
    await db.execute(
        delete(Message).where(Message.conversation_id == conversation_id)
    )
    
    await db.delete(conv)
    await db.commit()
    
    return {"status": "deleted"}




@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    payload: dict,
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    seq_result = await db.execute(
        select(func.coalesce(func.max(Message.sequence_number), 0) + 1)
        .where(Message.conversation_id == conversation_id)
    )
    user_seq = seq_result.scalar()
    
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=payload["message"],
        sequence_number=user_seq
    )
    db.add(user_msg)
    await db.commit()
    
    llm = get_llm_client()
    
    # Build messages based on conversation mode
    if conv.conversation_mode == ConversationMode.DOCUMENT_QA:
        docs_result = await db.execute(
            select(Document.id)
            .where(
                Document.conversation_id == conversation_id,
                Document.status == "COMPLETED"
            )
        )
        doc_ids = [row[0] for row in docs_result.all()]
        
        if not doc_ids:
            raise HTTPException(
                status_code=400, 
                detail="No processed documents available for this conversation"
            )
        
        # chunks from vector DB
        relevant_chunks = await RAGService.retrieve(
            query=payload["message"],
            document_ids=doc_ids,  
            top_k=3
        )
        
        context = "\n\n".join(relevant_chunks)
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions based ONLY on the provided context. If the answer is not in the context, say you don't know."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {payload['message']}"
            }
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": payload["message"]},
        ]
    
    async def event_generator():
        full_response = ""
        metadata = {
            "model": None,
            "finish_reason": None,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "conversation_mode": conv.conversation_mode.value
        }
        
        async for chunk in llm.stream_generate(
            messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        ):
            try:
                data = json.loads(chunk)
                
                if not metadata["model"]:
                    metadata["model"] = data.get("model")
                
                choice = data.get("choices", [{}])[0]
                content = choice.get("delta", {}).get("content", "")
                if content:
                    full_response += content
                    yield {"data": content}
                
                if choice.get("finish_reason"):
                    metadata["finish_reason"] = choice["finish_reason"]
                if "usage" in data:
                    metadata.update(data["usage"])
                    
            except json.JSONDecodeError:
                continue
        
        seq_result = await db.execute(
            select(func.coalesce(func.max(Message.sequence_number), 0) + 1)
            .where(Message.conversation_id == conversation_id)
        )
        assistant_seq = seq_result.scalar()
        
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            sequence_number=assistant_seq,
            tokens_used=metadata.get("total_tokens"),
            meta_data=metadata
        )
        db.add(assistant_msg)
        await db.commit()
        yield {"event": "done", "data": "[DONE]"}
    
    return EventSourceResponse(event_generator())