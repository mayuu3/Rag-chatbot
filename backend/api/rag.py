import os, json, faiss
from pathlib import Path
from api.embeddings_util import embed_texts


BASE = Path(__file__).resolve().parents[1]
FAISS_DIR = BASE / "data" / "faiss"
CHUNKS_DIR = BASE / "data" / "chunks"

FAISS_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

def chunk_text(text, chunk_size=300):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def build_faiss_index(user_id, chunks):
    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)
    dim = vectors.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, str(FAISS_DIR / f"{user_id}.index"))

    with open(CHUNKS_DIR / f"{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

def retrieve(user_id, query, k=5):
    idx_path = FAISS_DIR / f"{user_id}.index"
    meta_path = CHUNKS_DIR / f"{user_id}.json"

    if not idx_path.exists(): 
        return []

    index = faiss.read_index(str(idx_path))
    q_vec = embed_texts([query])[0]
    scores, idxs = index.search(q_vec.reshape(1, -1), k)

    meta = json.loads(meta_path.read_text())
    return [meta[i] for i in idxs[0]]

def summarize_chunks(chunks, length=600):
    full = " ".join([c["text"] for c in chunks])
    return full[:length] + "..."
