from pathlib import Path

import backoff
import elastic_transport
import psycopg2
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()


class AppConfig(BaseSettings):
    debug: bool = Field(..., env="DEBUG")
    chunk_size: int = Field(..., env="CHUNK_SIZE")
    etl_interval: int = Field(..., env="ETL_RUNS_INTERVAL")
    backoff_interval: float = Field(..., env="BACKOFF_MAX_RETRY_INTERVAL")
    es_index_name = "movies"
    json_storage_path = Path(__file__).resolve().parent / "storage" / "storage.json"


class PostgresDSN(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB_NAME")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(..., env="POSTGRES_PORT")
    options: str = Field(..., env="POSTGRES_OPTIONS")


class ElasticDSN(BaseSettings):
    host: str = Field(..., env="ELASTICSEARCH_HOST")
    port: int = Field(..., env="ELASTICSEARCH_PORT")


POSTGRES_DSN = PostgresDSN()
ELASTIC_DSN = ElasticDSN()
APP_CONFIG = AppConfig()

backoff_exceptions = (
    elastic_transport.ConnectionError,
    psycopg2.OperationalError,
    psycopg2.InterfaceError,
)

# backoff configured to wait indefinitely with at most max_value seconds between retries
BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": backoff_exceptions,
    "logger": "backoff",
    "max_value": APP_CONFIG.backoff_interval,
}
