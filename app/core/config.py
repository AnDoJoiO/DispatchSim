from pydantic import model_validator
from pydantic_settings import BaseSettings

_INSECURE_DEFAULT = "change-me-in-production"


class Settings(BaseSettings):
    APP_NAME: str = "Proyecto Dispatch"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./dispatch.db"
    ANTHROPIC_API_KEY: str = ""
    SECRET_KEY: str = _INSECURE_DEFAULT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Orígens permesos per CORS, separats per comes
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    @model_validator(mode="after")
    def _check_secret_key(self) -> "Settings":
        if not self.DEBUG and self.SECRET_KEY == _INSECURE_DEFAULT:
            raise ValueError(
                "SECRET_KEY no pot ser el valor per defecte en producció. "
                "Defineix SECRET_KEY al fitxer .env"
            )
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY ha de tenir com a mínim 32 caràcters."
            )
        return self

    class Config:
        env_file = ".env"


settings = Settings()
