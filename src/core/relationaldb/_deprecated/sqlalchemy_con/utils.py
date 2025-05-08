from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.config import POOL_SIZE, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USER

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,pool_size=POOL_SIZE)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
