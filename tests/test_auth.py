from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from tests.conftest import auth_header
from app.core.security import hash_password
from app.models.user import User, UserRole


class TestRegister:
    def test_register_success(self, client):
        res = client.post("/api/v1/auth/register", json={
            "username": "newuser", "password": "pass123",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == "newuser"
        assert data["role"] == "operador"

    def test_register_duplicate(self, client, operator_user):
        res = client.post("/api/v1/auth/register", json={
            "username": "testoperator", "password": "pass123",
        })
        assert res.status_code == 409

    def test_register_short_username(self, client):
        res = client.post("/api/v1/auth/register", json={
            "username": "ab", "password": "pass123",
        })
        assert res.status_code == 422

    def test_register_invalid_chars(self, client):
        res = client.post("/api/v1/auth/register", json={
            "username": "user@name!", "password": "pass123",
        })
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client, operator_user):
        res = client.post("/api/v1/auth/login", json={
            "username": "testoperator", "password": "oper123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testoperator"

    def test_login_wrong_password(self, client, operator_user):
        res = client.post("/api/v1/auth/login", json={
            "username": "testoperator", "password": "wrong",
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/v1/auth/login", json={
            "username": "ghost", "password": "pass",
        })
        assert res.status_code == 401

    def test_login_inactive_user(self, client, session):
        user = User(
            username="inactive", hashed_password=hash_password("pass123"),
            role=UserRole.OPERADOR, is_active=False,
        )
        session.add(user)
        session.commit()
        res = client.post("/api/v1/auth/login", json={
            "username": "inactive", "password": "pass123",
        })
        assert res.status_code == 403

    def test_login_expired_user(self, client, session):
        user = User(
            username="expired", hashed_password=hash_password("pass123"),
            role=UserRole.OPERADOR,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        session.add(user)
        session.commit()
        res = client.post("/api/v1/auth/login", json={
            "username": "expired", "password": "pass123",
        })
        assert res.status_code == 403

    def test_login_rate_limit(self, client, operator_user):
        for _ in range(5):
            client.post("/api/v1/auth/login", json={
                "username": "testoperator", "password": "wrong",
            })
        res = client.post("/api/v1/auth/login", json={
            "username": "testoperator", "password": "wrong",
        })
        assert res.status_code == 429


class TestMe:
    def test_me_authenticated(self, client, admin_token):
        res = client.get("/api/v1/auth/me", headers=auth_header(admin_token))
        assert res.status_code == 200
        assert res.json()["username"] == "testadmin"

    def test_me_no_token(self, client):
        res = client.get("/api/v1/auth/me")
        assert res.status_code in (401, 403)  # depends on bearer scheme handling
