import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()
Base = declarative_base() 

MYSQL_HOST = os.getenv("DATABASE_HOST", "localhost")
MYSQL_DATABASE_NAME = os.getenv("DATABASE_NAME", "n2b")
MYSQL_USER = os.getenv("DATABASE_USER", "root")
MYSQL_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE_NAME}?charset=utf8mb4"

# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,       # True면 SQL 로그 출력
    pool_size=5,
    max_overflow=10
)

# Session Factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))