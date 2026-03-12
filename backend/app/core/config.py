from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Admin Credentials
    ADMIN_EMAIL: str = "chirag@gmail.com"
    ADMIN_PASSWORD_HASH: str = "$2b$12$iFAaFEWqqfsQcXuCm9cYfe7GYCaz/oTSHzBl.lXIHIbHg5hh/R7Xu" # 123456

    class Config:
        env_file = ".env"

settings = Settings()