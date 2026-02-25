from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs: dict = {"echo": settings.DEBUG}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL: pool amb reconexió automàtica
    _engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)


def _sqlite_add_missing_columns() -> None:
    """Migració manual per SQLite: afegeix columnes noves sense perdre dades existents."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(app_user)"))
        columns = [row[1] for row in result]
        if "expires_at" not in columns:
            conn.execute(text("ALTER TABLE app_user ADD COLUMN expires_at DATETIME"))
            conn.commit()


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    if _is_sqlite:
        _sqlite_add_missing_columns()


def get_session():
    with Session(engine) as session:
        yield session
