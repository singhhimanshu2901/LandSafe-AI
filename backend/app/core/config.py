from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    ENV: str = "production"
    SECRET_KEY: str
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_ORIGINS: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
