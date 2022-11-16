import datetime
import uuid

from pydantic import BaseModel, validator


class Person(BaseModel):
    id: uuid.UUID
    name: str


class MovieDocument(BaseModel):
    id: uuid.UUID
    imdb_rating: float | None
    genre: list[str]
    title: str
    description: str
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[Person] | None
    writers: list[Person] | None
    modified: datetime.datetime

    @validator("director", "actors_names", "writers_names", pre=True)
    def not_none(cls, v):  # noqa: N805
        return v if v is not None else []
