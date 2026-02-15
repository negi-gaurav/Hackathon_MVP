from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Content Detection API"
    debug: bool = False
    model_dir: str = "../models"

    class Config:
        env_file = ".env"


settings = Settings()
