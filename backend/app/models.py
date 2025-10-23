from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.orm import declarative_base

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(DB_DIR, 'equiscan.db')}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()


class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String, default="")
    score = Column(Float, default=0.0)
    total_checks = Column(Integer, default=0)
    passes = Column(Integer, default=0)
    violations = Column(Integer, default=0)
    by_impact = Column(Text, default="{}")
    by_principle = Column(Text, default="{}")
    issues = Column(Text, default="[]")
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)
