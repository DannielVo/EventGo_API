# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.base import Base
import os

# Đọc URL từ .env hoặc dùng mặc định bên dưới
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:123456@localhost:5432/eventdb"
)

# Tạo engine kết nối đến PostgreSQL
engine = create_engine(DATABASE_URL)

# Tạo session để thao tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()