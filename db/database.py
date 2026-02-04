from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# =========================
# DB URL
# =========================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./slg.db"  # 기본값: 로컬 SQLite
)

# =========================
# Engine 생성
# =========================
engine = create_engine(
    DATABASE_URL,
    echo=False,  # True면 SQL 로그 출력
    future=True,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# =========================
# Session
# =========================
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

# =========================
# Base (모든 ORM 모델의 부모)
# =========================
Base = declarative_base()

# =========================
# FastAPI Dependency
# =========================
def get_db():
    """
    FastAPI 의존성 주입용 DB 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
