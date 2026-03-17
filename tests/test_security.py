import pytest
from jose import jwt

from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.config import settings


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert verify_password("mypassword", hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_unicode_password(self):
        hashed = hash_password("contraseña_ñ_àéïö")
        assert verify_password("contraseña_ñ_àéïö", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts
        assert verify_password("same", h1)
        assert verify_password("same", h2)


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token({"sub": 42, "role": "admin", "username": "test"})
        payload = decode_token(token)
        assert payload["sub"] == "42"  # sub is stringified
        assert payload["role"] == "admin"
        assert payload["username"] == "test"
        assert "exp" in payload

    def test_expired_token_raises(self):
        from datetime import datetime, timezone, timedelta
        token = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        with pytest.raises(Exception):  # JWTError / ExpiredSignatureError
            decode_token(token)

    def test_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_token("not.a.valid.token")

    def test_tampered_token_raises(self):
        token = create_access_token({"sub": 1})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(Exception):
            decode_token(tampered)
