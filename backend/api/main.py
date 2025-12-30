import os, shutil, json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader

from api.rag import chunk_text, build_faiss_index, retrieve
from api.llm import generate_answer

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA = Path("/tmp/data")
UPLOADS = DATA / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)

from api.auth import register_user, login_user

@app.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    return register_user(name, email, password)


@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...)
):
    return login_user(email, password)

@app.post("/upload")
async def upload(token: str = Form(...), file: UploadFile = File(...)):
    user_dir = UPLOADS / token
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"status": "uploaded", "filename": file.filename}

@app.post("/process")
def process(token: str = Form(...)):
    user_dir = UPLOADS / token
    chunks = []

    for pdf in user_dir.glob("*.pdf"):
        reader = PdfReader(pdf)
        text = "\n".join([p.extract_text() or "" for p in reader.pages])

        for c in chunk_text(text)[:40]:
            chunks.append({"text": c})

    if chunks:
        build_faiss_index(token, chunks)

    return {"chunks": len(chunks)}

@app.post("/chat")
def chat(token: str = Form(...), query: str = Form(...)):
    retrieved = retrieve(token, query)

    context = "\n".join([r["text"] for r in retrieved]) if retrieved else ""

    prompt = f"""
Answer the question. Use document context if available.

CONTEXT:
{context}

QUESTION:
{query}
"""

    answer = generate_answer(prompt)
    return {"answer": answer}
