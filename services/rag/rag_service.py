import hashlib
from db.chroma_client import collection
from services.rag.embeddings import embed_text


class RAGService:

    @staticmethod
    async def add_document_chunks(document_id: str, chunks: list[str]):
        for idx, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{document_id}_{idx}"],
                embeddings=[embed_text(chunk)],
                documents=[chunk],
                metadatas=[{"document_id": document_id}]
            )

    @staticmethod
    async def retrieve(query: str, document_ids: list[str] = None, top_k: int = 3):
        query_embedding = embed_text(query)
        
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        return results["documents"][0] if results["documents"] else []
