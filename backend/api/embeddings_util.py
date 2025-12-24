# api/embeddings_util.py
from sentence_transformers import SentenceTransformer
import os

MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL)
    return _model

def embed_texts(texts: list):
    model = get_model()
    return model.encode(texts, convert_to_numpy=True)
