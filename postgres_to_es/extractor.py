import datetime
import logging
from contextlib import closing
from typing import Iterator

import pydantic

import postgres_to_es.models
import postgres_to_es.utils
from postgres_to_es.settings import APP_CONFIG

logger = logging.getLogger(__name__)


def extract_postgres(
    timestamp: str | None,
) -> Iterator[tuple[postgres_to_es.models.MovieDocument, ...]]:
    """Extract records from PostgreSQL.

    Retrieves all records that were modified after timestamp.

    Args:
        timestamp: A timestamp after which to retrieve records. If None, datetime.min
        used instead. Format of timestamp must be accepted by PostgreSQL.

    Yields:
        A tuple of pydantic models. Tuple contains at most APP_CONFIG.chunk_size
        elements.
    """
    if timestamp is None:
        timestamp = datetime.datetime.min.isoformat()

    query = postgres_to_es.utils.get_query(timestamp)
    with closing(postgres_to_es.utils.get_postgres_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            while rows := cursor.fetchmany(APP_CONFIG.chunk_size):
                try:
                    yield tuple(
                        postgres_to_es.models.MovieDocument(**row) for row in rows
                    )
                except pydantic.ValidationError:
                    logger.exception(
                        "Error on validation. Check definitions of model and SQL query.",
                    )
