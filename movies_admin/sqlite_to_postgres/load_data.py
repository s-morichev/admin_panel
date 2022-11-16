#!/usr/bin/env python
"""Module to load data from SQLite to PostgreSQL."""
import logging
import sqlite3
import sys
from contextlib import closing

import psycopg2
import pydantic
from psycopg2.extensions import connection
from psycopg2.extras import register_uuid
from sqlite_to_postgres import extrators, savers, settings


def setup_logging() -> None:
    """Do basic logging setup."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(level=level, format=log_format)


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: connection) -> None:
    """Load data from SQLite to PostgreSQL.

    Args:
        sqlite_conn: A connection to SQLite database. Connection must have
            row_factory that returns dict-like rows, e.g. sqlite3.Row
        pg_conn: A connection to PostgreSQL database.
    """
    postgres_saver = savers.PostgresSaver(pg_conn)
    sqlite_extractor = extrators.SQLiteExtractor(sqlite_conn)

    movies_data = sqlite_extractor.extract_movies(settings.SQLITE_TO_POSTGRES_MODELS)

    try:
        postgres_saver.save_all_data(movies_data, settings.SQLITE_TO_POSTGRES_MODELS)
        logger.info(
            "Data copied from %s to postgres db '%s'",
            settings.SQLITE_PATH,
            settings.PG_DSN.dbname,
        )
    except sqlite3.Error:
        logger.exception("Error during execution of SQL to extract data")
        sys.exit(1)
    except pydantic.ValidationError:
        logger.exception("Error on model validation")
        sys.exit(1)
    except psycopg2.Error:
        logger.exception("Error during execution of SQL to save data")
        sys.exit(1)


def main() -> None:
    # sqlite.connect() creates empty database, if there is no file
    # so check it to prevent creating unnecessary files
    if not settings.SQLITE_PATH.is_file():
        logger.error(f"Database file {settings.SQLITE_PATH} doesn't exist")
        sys.exit(1)

    with closing(sqlite3.connect(settings.SQLITE_PATH)) as sql_conn:
        try:
            with closing(psycopg2.connect(**settings.PG_DSN.dict())) as pg_conn:
                sql_conn.row_factory = sqlite3.Row
                register_uuid(conn_or_curs=pg_conn)
                with sql_conn, pg_conn:
                    load_from_sqlite(sql_conn, pg_conn)
        except psycopg2.OperationalError:
            logger.exception("Cannot connect to PostgreSQL database")
            sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    main()
