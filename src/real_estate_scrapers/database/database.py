"""Interactions via the Postgres database via SQLAlchemy."""
from typing import Any, List, Optional

from loguru import logger
from sqlalchemy import create_engine, inspect  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore
from sqlalchemy.orm import Session, sessionmaker  # type: ignore

from real_estate_scrapers.database.config import get_database_url
from real_estate_scrapers.models import RealEstateDBItem, SQLBaseModel


class DatabaseHandler:
    """DB Handler Class"""

    def __init__(self, database_url: str, base: DeclarativeMeta, table_names: Optional[List[str]] = None) -> None:
        self.engine = create_engine(database_url)
        self.base = base
        self.db_session = sessionmaker(bind=self.engine)
        self._current_session: Optional[Session] = None
        self._table_names = table_names if table_names is not None else []
        self.__init_tables()

    def __init_tables(self) -> None:
        """Creates the tables in the database if they do not exist."""
        tables_exist = all(inspect(self.engine).has_table(table_name) for table_name in self._table_names)
        if tables_exist:
            logger.debug("Tables already exist in the database.")
        else:
            logger.debug("Creating tables in the database.")
            self.base.metadata.drop_all(self.engine)
            self.base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """Drop all tables in the database."""
        logger.debug("Dropping tables in the database.")
        self.base.metadata.drop_all(self.engine)

    def create_session(self) -> Session:
        """
        Returns: A new ``Session``.
        """
        return self.db_session()

    def __open_session(self) -> None:
        """
        Opens a new session.

        Raises: ``RuntimeError`` if the session is already open.
        """
        if self._current_session is not None and self._current_session.is_active:
            logger.error("Session is already open.")
            raise RuntimeError("Session is already open.")
        self._current_session = self.db_session()

    def __close_session(self) -> None:
        """
        Closes the current session.

        Raises: ``RuntimeError`` if the session does not exist or is already closed.
        """
        if self._current_session is not None and self._current_session.is_active:
            self._current_session.close()
        else:
            logger.error("Session is None or it is already closed.")
            raise RuntimeError("Session is None or it is already closed.")

    def __enter__(self) -> Session:
        """Opens and returns a new ``Session``."""
        self.__open_session()
        return self._current_session

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Closes the current session."""
        self.__close_session()

    def close(self) -> None:
        """Closes the handler."""
        logger.debug("Closing the database handler.")
        self.db_session.close_all()
        self.engine.dispose()


db_handler = DatabaseHandler(
    database_url=get_database_url(), base=SQLBaseModel, table_names=[RealEstateDBItem.__tablename__]
)
