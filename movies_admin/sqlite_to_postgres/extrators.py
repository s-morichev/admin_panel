"""Data extractors for relational databases.

Only sqlite extractor so far.
"""
import logging
import sqlite3
from collections.abc import Iterable
from typing import Generator

import pydantic
from sqlite_to_postgres import models

logger = logging.getLogger(__name__)


def _row_to_str(row: sqlite3.Row) -> str:
    """Convert sqlite3.Row instance to string.

    Args:
        row: A row to convert.

    Returns:
        String representation of row.
    """
    return ", ".join(f"{column}: {row[column]}" for column in row.keys())


class SQLiteExtractor:
    """Data extractor for sqlite databases.

    Attributes:
        conn: A connection to sqlite database. Connection must have
            row_factory that returns dict-like rows, e.g. sqlite3.Row
    """

    def __init__(self, conn: sqlite3.Connection):  # noqa: D107
        self.conn = conn

    def extract_table(
        self,
        table_model: type[models.DBTable],
    ) -> Generator[models.DBTable, None, None]:
        """Generate rows from a table.

        Args:
            table_model: A pydantic model class that represents table.

        Yields:
            A pydantic model with row data.

        Raises:
            sqlite3.OperationalError: If occurred error on execution of SQL statement
                for retrieving data from database.
            pydantic.ValidationError: If occurred error on model creation.
        """
        table_name = table_model.table_name
        sql = f"SELECT * FROM {table_name};"  # noqa: S608
        try:
            cursor = self.conn.execute(sql)
        except sqlite3.OperationalError:
            logger.error(
                "Error during SQL execution. Check if table name is correct in statement: %s ",
                sql,
            )
            raise

        for row in cursor:
            try:
                yield table_model(**row)
            except pydantic.ValidationError:
                logger.error(
                    "Validation error in table %s on row {%s})",
                    table_name,
                    _row_to_str(row),
                )
                raise

    def extract_movies(
        self,
        table_models: Iterable[type[models.DBTable]],
    ) -> tuple[Generator[models.DBTable, None, None], ...]:
        """Extract data from multiple tables.

        Args:
            table_models: A pydantic models that represents tables to extract data.

        Returns:
            A tuple containing generator for each table. Generators are
            ordered accordingly to table_models.
        """
        return tuple(self.extract_table(table_model) for table_model in table_models)
