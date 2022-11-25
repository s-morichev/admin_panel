from pathlib import Path
from typing import Callable, Generator, TypedDict

import backoff
import elastic_transport
import psycopg2
from pydantic import BaseSettings, Field


class AppConfig(BaseSettings):
    debug: bool
    chunk_size: int
    etl_interval: int = Field(..., env="ETL_RUNS_INTERVAL")
    backoff_interval: float = Field(..., env="BACKOFF_MAX_RETRY_INTERVAL")
    es_index_name = "movies"
    json_storage_path = Path(__file__).resolve().parent / "storage" / "storage.json"


class PostgresDSN(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB_NAME")
    user: str
    password: str
    host: str
    port: int
    options: str

    class Config:
        env_prefix = "postgres_"


class ElasticDSN(BaseSettings):
    host: str
    port: int

    class Config:
        env_prefix = "elasticsearch_"


POSTGRES_DSN = PostgresDSN()
ELASTIC_DSN = ElasticDSN()
APP_CONFIG = AppConfig()

backoff_exceptions = (
    elastic_transport.ConnectionError,
    psycopg2.OperationalError,
    psycopg2.InterfaceError,
)

# backoff configured to wait indefinitely with at most max_value seconds between retries
BACKOFF_CONFIG2 = {
    "wait_gen": backoff.expo,
    "exception": backoff_exceptions,
    "logger": "backoff",
    "max_value": APP_CONFIG.backoff_interval,
}


class BackoffParameters(TypedDict):
    wait_gen: Callable[..., Generator[float, None, None]]
    exception: tuple[type[Exception], ...]
    logger: str
    max_value: float


BACKOFF_CONFIG: BackoffParameters = {
    "wait_gen": backoff.expo,
    "exception": backoff_exceptions,
    "logger": "backoff",
    "max_value": APP_CONFIG.backoff_interval,
}
