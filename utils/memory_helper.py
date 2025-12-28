
from sqlalchemy import select
from db.models.conversation import Conversation
from db.models.message import Message


async def create_older_context(db, conversation:Conversation):

    #for short intial conversations (when summary is not available)
    msgs = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.sequence_number.desc())
        .limit(6)
    )
    
    messages = []
    if conversation.conversation_summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary:\n{conversation.conversation_summary}"
        })

    for m in reversed(msgs.scalars().all()):
        messages.append({"role": m.role, "content": m.content})

    return messages
