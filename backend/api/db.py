from sqlmodel import SQLModel, create_engine, Session, Field
from datetime import datetime
from typing import Optional
from pathlib import Path

DATABASE_URL = "sqlite:////tmp/app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password_hash: Optional[str] = None
    is_paid: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    filename: str
    filepath: str
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class History(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    title: str
    messages: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
