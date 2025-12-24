from fastapi import APIRouter, UploadFile, File, Form,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models.document import Document
from db.models.user import User
from db.models.conversation import Conversation
from utils.auth_helper import verify_user
from sqlalchemy import select
from fastapi.exceptions import HTTPException
import aiofiles
import os
from fastapi import BackgroundTasks
from services.rag.rag_service import RAGService
import PyPDF2
import io

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload", status_code=202)
async def upload_documents(
    files: list[UploadFile] = File(...),
    conversation_id: str = Form(...),
    user: User = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    # Verify conversation belongs to user
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conv = conv_result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    uploaded_docs = []
    
    for file in files:
        content = await file.read()
        file_size = len(content)
        
        doc = Document(
            conversation_id=conversation_id,
            user_id=user.id,
            name=file.filename,
            file_size=file_size,
            file_type=file.content_type,
            status="PROCESSING"
        )
        db.add(doc)
        await db.flush()  # doc.id without committing
        
        # Save to local storage for now (TODO: Move to S3)
        file_path = os.path.join(UPLOAD_DIR, f"{doc.id}_{file.filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        doc.storage_path = file_path

        background_tasks.add_task(process_document, doc.id, file_path, db)
        
        # TODO: Trigger Step Function for processing
        # await trigger_processing(doc.id)
        
        uploaded_docs.append({
            "document_id": doc.id,
            "name": doc.name,
            "status": doc.status
        })
    
    await db.commit()
    
    return {
        "documents": uploaded_docs,
        "total": len(uploaded_docs)
    }


async def process_document(document_id: str, file_path: str, db: AsyncSession):
    """Background task to chunk and embed document"""
    try:
        chunks = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        chunk_size = 500
        overlap = 50
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
        
        await RAGService.add_document_chunks(document_id, chunks)
        
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        doc = result.scalar_one_or_none()
        if doc:
            doc.status = "COMPLETED"
            doc.meta_data = {"chunks_count": len(chunks)}
            await db.commit()
            
    except Exception as e:
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        doc = result.scalar_one_or_none()
        if doc:
            doc.status = "FAILED"
            doc.error_message = str(e)
            await db.commit()

