from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Proyecto Dispatch"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./dispatch.db"
    ANTHROPIC_API_KEY: str = ""
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
