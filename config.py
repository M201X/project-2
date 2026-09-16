from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./database.db"
    secret_key: str = "my-secret-key"
    access_token_expire_minutes: int = 30


settings = Settings()

