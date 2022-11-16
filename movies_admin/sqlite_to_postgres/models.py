"""Pydantic models for tables in database."""
import datetime
import uuid
from typing import ClassVar, Literal

from pydantic import BaseModel, Field, constr, validator


def _replace_none_with_empty_string(text: str | None) -> str:
    return "" if text is None else text


def not_null_text_validator(field: str) -> classmethod:
    """Return reusable validator that replaces None with empty string.

    Args:
        field: Name of field.
    """
    decorator = validator(field, allow_reuse=True, pre=True)
    return decorator(_replace_none_with_empty_string)


class DBTable(BaseModel):
    """Base model for database tables.

    Each instance attribute corresponds to column in a database.
    If a database to read from has different column name, then write
    that name as an alias to field. For example::
        class Table(DBTable):
            title: str
            quantity: int = Field(alias="amount")

        cursor.execute("SELECT title, amount FROM table")
        row_data = Table(**cursor.fetchone())

    Attributes:
        table_name: Name of table in database.
    """

    table_name: ClassVar[str]

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def get_field_names(cls) -> str:
        """Return comma separated field names."""
        return ", ".join(cls.__fields__.keys())


class MoviesDBTable(DBTable):
    id: uuid.UUID


class TimestampedMixin(BaseModel):
    created: datetime.datetime = Field(alias="created_at")
    modified: datetime.datetime = Field(alias="updated_at")


class Filmwork(MoviesDBTable, TimestampedMixin):
    title: constr(max_length=255)
    description: str
    creation_date: datetime.date | None
    rating: float | None
    type: Literal["movie", "tv-show"]
    table_name = "film_work"

    _description_not_null = not_null_text_validator("description")


class Person(MoviesDBTable, TimestampedMixin):
    full_name: constr(max_length=255)
    table_name = "person"


class Genre(MoviesDBTable, TimestampedMixin):
    name: constr(max_length=255)
    description: str
    table_name = "genre"

    _description_not_null = not_null_text_validator("description")


class GenreFilmwork(MoviesDBTable):
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created: datetime.datetime = Field(alias="created_at")
    table_name = "genre_film_work"


class PersonFilmwork(MoviesDBTable):
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: Literal["actor", "director", "writer"]
    created: datetime.datetime = Field(alias="created_at")
    table_name = "person_film_work"
