from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    YOUTUBE_API_KEY: str
    DATABASE_URL: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


config = Settings()
