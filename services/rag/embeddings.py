
from sentence_transformers import SentenceTransformer

_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str):
    return _embedding_model.encode(text).tolist()
