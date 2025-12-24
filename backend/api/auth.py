# api/auth.py
import os, time, bcrypt, jwt
from fastapi import HTTPException
from sqlmodel import select
from api.db import get_session, User


JWT_SECRET = os.getenv("JWT_SECRET", "SECRET_KEY")
JWT_ALGO = "HS256"
JWT_EXP = 60 * 60 * 24 * 7

def hash_password(pw: str):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = int(time.time()) + JWT_EXP
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def register_user(name, email, password):
    with get_session() as s:
        exists = s.exec(select(User).where(User.email == email)).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email exists")

        hashed = hash_password(password)
        user = User(name=name, email=email, password_hash=hashed)
        s.add(user); s.commit(); s.refresh(user)

        token = create_token({"user_id": user.id, "email": user.email})
        return {"user": user, "token": token}

def login_user(email, password):
    with get_session() as s:
        user = s.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token({"user_id": user.id, "email": user.email})
        return {"user": user, "token": token}
