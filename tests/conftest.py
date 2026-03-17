import os, pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

# Force test settings before importing app
os.environ.update({
    "DATABASE_URL": "sqlite:///./test.db",
    "SECRET_KEY": "test-secret-key-with-at-least-32-chars!!",
    "DEBUG": "true",
    "ANTHROPIC_API_KEY": "test-key",
    "DispatchSimKeyOpenAI": "test-key",
})

from app.main import app  # noqa: E402
from app.db.session import engine, get_session  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.core.rate_limit import login_limiter, chat_limiter, transcribe_limiter, tts_limiter  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh tables for each test, drop after. Reset rate limiters."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
    # Reset rate limiters between tests
    for limiter in (login_limiter, chat_limiter, transcribe_limiter, tts_limiter):
        limiter._calls.clear()


@pytest.fixture
def session():
    with Session(engine) as s:
        yield s


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_user(session):
    user = User(
        username="testadmin",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def operator_user(session):
    user = User(
        username="testoperator",
        hashed_password=hash_password("oper123"),
        role=UserRole.OPERADOR,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    res = client.post("/api/v1/auth/login", json={
        "username": "testadmin", "password": "admin123",
    })
    return res.json()["access_token"]


@pytest.fixture
def operator_token(client, operator_user):
    res = client.post("/api/v1/auth/login", json={
        "username": "testoperator", "password": "oper123",
    })
    return res.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
