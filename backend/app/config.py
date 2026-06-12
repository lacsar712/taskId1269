import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://water_user:water123@localhost:3306/water_treatment?charset=utf8mb4"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "water-treatment-secret-key-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()
