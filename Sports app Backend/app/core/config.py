from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    oracle_user: str
    oracle_password: str
    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service_name: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()