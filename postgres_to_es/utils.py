import json
import logging
from contextlib import closing
import http
from pathlib import Path
from typing import Any

import backoff
import psycopg2
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from settings import BACKOFF_CONFIG, ELASTIC_DSN, POSTGRES_DSN

logger = logging.getLogger(__name__)


@backoff.on_exception(**BACKOFF_CONFIG)
def get_postgres_connection() -> connection:
    """Return PostgreSQL connection.

    Uses backoff to wait until PostgreSQL is up.

    Returns:
        PostgeSQL connection.
    """
    conn = psycopg2.connect(**POSTGRES_DSN.dict(), cursor_factory=DictCursor)
    conn.autocommit - True
    return conn


@backoff.on_exception(**BACKOFF_CONFIG)
def get_elasticsearch_client() -> Elasticsearch:
    """Return Elasticsearch client.

    Uses backoff to wait until Elasticsearch is up.

    Returns:
        Elasticsearch client.
    """
    es = Elasticsearch(f"http://{ELASTIC_DSN.host}:{ELASTIC_DSN.port}")
    # make request to elasticsearch to check if it is running
    # if it isn't then elasticsearch raises ConnectionError which is caught by backoff
    es.info()
    return es


def load_index_definition(file_path: Path) -> dict[str, Any]:
    """Load Elasticsearch index definition from json file.

    Args:
        file_path: Path to file.

    Returns:
        A dict containing Elasticsearch index definition.
    """
    try:
        with file_path.open("r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.exception("Couldn't create index. No file %s", file_path)
        raise
    except json.JSONDecodeError:
        logger.exception("Invalid index definition in file %s", file_path)
        raise


@backoff.on_exception(**BACKOFF_CONFIG)
def create_elasticsearch_index(index_name: str) -> None:
    """Create Elasticsearch index.

    Definition of index must be in json file in directory elasticsearch_indices.
    Name of index and name of file must be same.

    Args:
        index_name: Name of index.
    """
    path = (
        Path(__file__).resolve().parent / "elasticsearch_indices" / f"{index_name}.json"
    )
    index_definition = load_index_definition(path)

    with closing(get_elasticsearch_client()) as es:
        es.options(ignore_status=http.HTTPStatus.BAD_REQUEST).indices.create(
            index=index_name,
            settings=index_definition.get("settings"),
            mappings=index_definition.get("mappings"),
        )


def get_query(timestamp: str) -> str:
    """Return SQL query for extracting records.

    Args:
        timestamp: A timestamp to substitute into query.

    Returns:
        SQL query.
    """
    return f"""
SELECT
    f.id,
    f.rating AS imdb_rating,
    ARRAY_AGG(DISTINCT g.name) AS genre,
    f.title,
    f.description,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') AS director,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
        FILTER (WHERE pfw.role = 'actor') AS actors,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
        FILTER (WHERE pfw.role = 'writer') AS writers,
    GREATEST(f.modified, MAX(p.modified), MAX(g.modified)) AS modified
FROM
    film_work AS f
    LEFT JOIN genre_film_work AS gfw ON f.id = gfw.film_work_id
    LEFT JOIN genre AS g ON gfw.genre_id = g.id
    LEFT JOIN person_film_work AS pfw ON f.id = pfw.film_work_id
    LEFT JOIN person AS p ON pfw.person_id = p.id
WHERE
    GREATEST(f.modified, p.modified, g.modified) > '{timestamp}'
GROUP BY f.id
ORDER BY modified ASC
    """
