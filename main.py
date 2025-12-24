from fastapi import FastAPI
from api import conversation, document,user

app = FastAPI(title="BOT GPT Backend")

app.include_router(conversation.router, prefix="/conversations")
app.include_router(document.router, prefix="/documents")
app.include_router(user.router, prefix="/user")



@app.get("/health")
async def health():
    return {"status": "ok"}
