"""Settings for loading data from SQLite to PostgreSQL."""
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, Field
from sqlite_to_postgres import models

load_dotenv()


class PostgresDSN(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB_NAME")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(..., env="POSTGRES_PORT")
    options: str = Field(..., env="POSTGRES_OPTIONS")


PG_DSN = PostgresDSN()

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "db.sqlite"
DEBUG = os.getenv("DEBUG", False) == "True"

SQLITE_TO_POSTGRES_MODELS = (
    models.Filmwork,
    models.Person,
    models.Genre,
    models.PersonFilmwork,
    models.GenreFilmwork,
)
