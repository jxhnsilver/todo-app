from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    @property
    def sync_database_url(self) -> str:
        return self._build_database_url("postgresql+psycopg")

    @property
    def async_database_url(self):
        return self._build_database_url("postgresql+asyncpg")


    @property
    def redis_url(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                username=self.REDIS_USER,
                password=self.REDIS_PASSWORD,
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=str(self.REDIS_DB),
            )
        )

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def _build_database_url(self, drivername: str) -> str:
        return URL.create(
            drivername=drivername,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)


settings = Settings()  # type: ignore[call-arg]
