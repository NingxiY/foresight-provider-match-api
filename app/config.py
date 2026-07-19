from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        # The root .env is shared with docker-compose (e.g. VITE_API_BASE_URL,
        # used only for the frontend build arg) — ignore vars this model
        # doesn't declare instead of failing startup on them.
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
