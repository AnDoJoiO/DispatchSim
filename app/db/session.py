import os

from alembic import command as alembic_command
from alembic.config import Config
from sqlalchemy import event, inspect, text
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

# SQLite: activar PRAGMA foreign_keys per a CASCADE/SET NULL
if _is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

_ALEMBIC_INI = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")
)


def _get_alembic_config() -> Config:
    return Config(_ALEMBIC_INI)


def create_db_and_tables() -> None:
    """Inicialitza l'esquema de la BD amb Alembic.

    - Primera execució (sense alembic_version): crea totes les taules
      via SQLModel.metadata.create_all i marca la BD com a 'head'.
    - Execucions posteriors: aplica les migracions pendents amb upgrade head.
    """
    existing_tables = inspect(engine).get_table_names()
    cfg = _get_alembic_config()

    if "alembic_version" not in existing_tables:
        # BD nova o anterior a Alembic: crear taules i estampar baseline
        SQLModel.metadata.create_all(engine)
        alembic_command.stamp(cfg, "head")
    else:
        # Alembic ja actiu: aplicar migracions pendents
        alembic_command.upgrade(cfg, "head")


def get_session():
    with Session(engine) as session:
        yield session
