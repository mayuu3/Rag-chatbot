import os
from dotenv import load_dotenv

# FORCE LOAD .env FROM BACKEND ROOT
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

print("DEBUG — ENV PATH LOADED:", ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

print("DEBUG — API KEY LOADED:", os.getenv("GROQ_API_KEY"))

import os, shutil, json
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from PyPDF2 import PdfReader

from api.auth import register_user, login_user, decode_token
from api.db import init_db, get_session, Document, History
from api.rag import chunk_text, build_faiss_index, retrieve, summarize_chunks
from api.llm import generate_answer   # ✅ NEW

# -----------------------------
# FASTAPI APP INIT
# -----------------------------
app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA = Path(__file__).resolve().parents[1] / "data"
UPLOADS = DATA / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)

# -----------------------------
# AUTH
# -----------------------------
@app.post("/register")
def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    return register_user(name, email, password)

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    return login_user(email, password)

@app.post("/guest")
def guest():
    token = "guest_" + os.urandom(8).hex()
    return {"token": token}

# -----------------------------
# UPLOAD DOCUMENTS
# -----------------------------
@app.post("/upload")
async def upload(token: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    user = decode_token(token) if not token.startswith("guest_") else {"user_id": token}
    user_id = user["user_id"]

    user_dir = UPLOADS / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    with get_session() as s:
        doc = Document(
            user_id=str(user_id),
            filename=file.filename,
            filepath=str(file_path)
        )
        s.add(doc)
        s.commit()

    return {"status": "uploaded", "filename": file.filename}


# -----------------------------
# PROCESS DOCUMENTS (CHUNK + FAISS)
# -----------------------------
@app.post("/process")
def process(token: str = Form(...)):
    user = decode_token(token) if not token.startswith("guest_") else {"user_id": token}
    user_id = user["user_id"]

    user_dir = UPLOADS / str(user_id)
    if not user_dir.exists():
        raise HTTPException(404, "No files uploaded")

    chunks = []
    with get_session() as s:
        docs = s.exec(select(Document).where(Document.user_id == str(user_id))).all()

        for d in docs:
            if d.filename.lower().endswith(".pdf"):
                text = "\n".join([(p.extract_text() or "") for p in PdfReader(d.filepath).pages])
            else:
                text = Path(d.filepath).read_text(errors="ignore")

            for c in chunk_text(text):
                chunks.append({"doc_id": d.id, "text": c})

    build_faiss_index(user_id, chunks)
    return {"chunks": len(chunks)}

# -----------------------------
# CHAT (RAG + GROQ LLM)
# -----------------------------
@app.post("/chat")
def chat(token: str = Form(...), query: str = Form(...)):
    # Identify user
    user = decode_token(token) if not token.startswith("guest_") else {"user_id": token}
    user_id = user["user_id"]

    # Retrieve from FAISS
    retrieved = retrieve(user_id, query)
    context = "\n".join([r["text"] for r in retrieved])

    # Build prompt for LLM
    prompt = f"""
You are a helpful AI assistant.

Use this DOCUMENT CONTEXT when answering.
If context does not contain information, answer normally.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    # Call LLM
    answer = generate_answer(prompt)

    # Save history (only registered users)
    if not str(user_id).startswith("guest_"):
        with get_session() as s:
            rec = History(
                user_id=str(user_id),
                title=query[:50],
                messages=json.dumps([{"q": query, "a": answer}])
            )
            s.add(rec)
            s.commit()

    return {"answer": answer, "sources": retrieved}

# -----------------------------
# HISTORY
# -----------------------------
@app.get("/history")
def history(token: str):
    if token.startswith("guest_"):
        return {"history": []}

    user = decode_token(token)
    user_id = user["user_id"]

    with get_session() as s:
        rows = s.exec(select(History).where(History.user_id == str(user_id))).all()
        return {"history": [
            {"title": r.title, "messages": r.messages, "created_at": str(r.created_at)}
            for r in rows
        ]}

# -----------------------------
# SUMMARIZE DOCUMENTS
# -----------------------------
@app.post("/summarize")
def summarize(token: str = Form(...)):
    user = decode_token(token) if not token.startswith("guest_") else {"user_id": token}
    user_id = user["user_id"]

    path = DATA / "chunks" / f"{user_id}.json"
    if not path.exists():
        return {"summary": "No documents"}

    chunks = json.loads(path.read_text())
    return {"summary": summarize_chunks(chunks)}
