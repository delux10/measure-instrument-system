from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "测量仪器全生命周期管理系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/measure_instruments"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:80"]
    ADMIN_PASSWORD: str = ""
    SYSTEM_MANAGER_PASSWORD: str = ""

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    CALIBRATION_WARN_DAYS: list = [30, 15, 7]

    class Config:
        env_file = ".env"


settings = Settings()
