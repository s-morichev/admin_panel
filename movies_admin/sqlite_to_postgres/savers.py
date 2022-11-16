"""Data savers for relational databases.

Only PostgreSQL saver so far.
"""
import logging
from collections.abc import Iterable

import psycopg2.errors
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from sqlite_to_postgres import models

logger = logging.getLogger(__name__)


class PostgresSaver:
    """Data saver for postgresql databases.

    Attributes:
        conn: A connection to PostgreSQL database.
    """

    def __init__(self, conn: connection):  # noqa: D107
        self.conn = conn

    def save_table(
        self,
        rows: Iterable[models.DBTable],
        table_model: type[models.DBTable],
        chunk_size: int = 1000,
    ) -> None:
        """Save data to a table.

        Args:
            rows: Contains data as pydantic model.
            table_model: A pydantic model class that represents table.
            chunk_size: Maximum number of rows to save at once. If there are
                more rows the method will make more than one query to database.

        Raises:
            psycopg2.errors.UndefinedTable: If there is invalid table name for
                saving data in database.
            psycopg2.errors.UndefinedColumn: If there is invalid column name for
                saving data in database.
        """
        table_name = table_model.table_name
        column_names = table_model.get_field_names()
        sql = (
            f"INSERT INTO {table_name} ({column_names}) VALUES %s "
            f"ON CONFLICT (id) DO NOTHING;"
        )
        args = (tuple(column_value for _, column_value in row) for row in rows)

        with self.conn.cursor() as cursor:
            try:
                execute_values(cursor, sql, args, page_size=chunk_size)
            except psycopg2.errors.UndefinedTable:
                logger.error(
                    "Error during SQL execution. Check if table name is correct in statement: %s ",
                    sql,
                )
                raise
            except psycopg2.errors.UndefinedColumn:
                logger.error(
                    "Error during SQL execution. Check if column names are correct in statement: %s ",
                    sql,
                )
                raise

    def save_all_data(
        self,
        data_to_save: Iterable[Iterable[models.DBTable]],
        table_models: Iterable[type[models.DBTable]],
        chunk_size: int = 1000,
    ) -> None:
        """Save data to multiple tables.

        Args:
            data_to_save: An iterable
            table_models: A pydantic models that represents tables to extract data.
            chunk_size: Maximum number of rows to save at once. See save_table().
        """
        for rows, table_model in zip(data_to_save, table_models):
            self.save_table(rows, table_model, chunk_size=chunk_size)
