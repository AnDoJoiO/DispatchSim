from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def add_missing_columns(engine):
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(app_user)"))
        columns = [row[1] for row in result]
        if "expires_at" not in columns:
            conn.execute(text("ALTER TABLE app_user ADD COLUMN expires_at DATETIME"))
            conn.commit()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    add_missing_columns(engine)


def get_session():
    with Session(engine) as session:
        yield session
