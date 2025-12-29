import json, faiss
from pathlib import Path
from api.embeddings_util import embed_texts

DATA = Path("/tmp/data")


FAISS_DIR = DATA / "faiss"
CHUNKS_DIR = DATA / "chunks"

FAISS_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

def chunk_text(text, chunk_size=120):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def build_faiss_index(user_id, chunks):
    if not chunks:
        return

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, str(FAISS_DIR / f"{user_id}.index"))
    with open(CHUNKS_DIR / f"{user_id}.json", "w") as f:
        json.dump(chunks, f)

def retrieve(user_id, query, k=5):
    idx = FAISS_DIR / f"{user_id}.index"
    meta = CHUNKS_DIR / f"{user_id}.json"

    if not idx.exists():
        return []

    index = faiss.read_index(str(idx))
    qv = embed_texts([query])

    _, ids = index.search(qv, k)
    data = json.loads(meta.read_text())

    return [data[i] for i in ids[0] if i < len(data)]
