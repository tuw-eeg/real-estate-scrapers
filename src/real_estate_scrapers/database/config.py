"""Loads the database configuration from the config file."""
import configparser
from abc import ABC, abstractmethod
from os import environ
from pathlib import Path
from typing import NamedTuple, Optional

from loguru import logger


class DBConfig(NamedTuple):
    """
    A typed dictionary that contains the database configuration.
    """

    database: str
    host: str
    port: int
    user: str
    password: str

    def __repr__(self) -> str:
        return (
            f"DBConfig("
            f"database={self.database}, "
            f"host={self.host}, "
            f"port={self.port}, "
            f"user={self.user}, "
            f"password={len(self.password) * '*'})"
        )


class DBConfigProvider(ABC):
    """
    Interface for a database configuration provider.
    """

    @abstractmethod
    def get_config(self) -> DBConfig:
        """
        Returns: the database configuration
        """
        raise NotImplementedError


class DBConfigProviderFileBasedImpl(DBConfigProvider):
    """
    A database configuration provider that loads the configuration from a `.cfg` file.

    Expected fields per section:

    **connection**
        - database
        - host
        - port

    **credentials**
        - user
        - password
    """

    def __init__(self, config_path: Path):
        """
        Args:
            config_path: the path to the configuration file
        """
        self._config_path = config_path

    def get_config(self) -> DBConfig:
        """
        Returns: the database configuration
        """
        config = self._get_config_object()
        try:
            return DBConfig(
                database=config.get("connection", "database"),
                host=config.get("connection", "host"),
                port=int(config.get("connection", "port")),
                user=config.get("credentials", "user"),
                password=config.get("credentials", "password"),
            )
        except configparser.Error as e:
            raise ValueError(f"Error while parsing the configuration file: {e}") from e

    def _get_config_object(self) -> configparser.ConfigParser:
        """
        Loads a configuration file into a `configparser.ConfigParser`
        object based on the specified file path.

        Returns: the `configparser.ConfigParser` object
        """
        config = configparser.ConfigParser()
        config.read(self._config_path)
        return config


class DBConfigProviderEnvVarBasedImpl(DBConfigProvider):
    """
    A database configuration provider that loads the configuration from environment variables.

    Expected environment variables:

    - `POSTGRES_DB`
    - `POSTGRES_HOST`
    - `POSTGRES_PORT`
    - `POSTGRES_USER`
    - `POSTGRES_PASSWORD`
    """

    required_env_vars = (
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )

    def get_config(self) -> DBConfig:
        """
        Returns: the database configuration
        """
        if not _env_vars_available():
            raise ValueError(
                f"Missing one of the following environment variables: "
                f"{DBConfigProviderEnvVarBasedImpl.required_env_vars}"
            )
        return DBConfig(
            database=environ["POSTGRES_DB"],
            host=environ["POSTGRES_HOST"],
            port=int(environ["POSTGRES_PORT"]),
            user=environ["POSTGRES_USER"],
            password=environ["POSTGRES_PASSWORD"],
        )


def _env_vars_available() -> bool:
    """
    Returns: `True` if all required environment variables for the Postgres connection are set, `False` otherwise
    """
    return all(env_var in environ for env_var in DBConfigProviderEnvVarBasedImpl.required_env_vars)


def _create_database_url_from_config(cfg: DBConfig) -> str:
    """
    Args:
        cfg: The database configuration.

    Returns: The database URL.
    """
    return f"postgresql://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}"


DEFAULT_PATH = Path(__file__).parent.parent.parent / "db.cfg"


def get_db_config(config_path: Optional[Path] = DEFAULT_PATH) -> DBConfig:
    """
    Returns the database configuration either from a configuration file or from environment variables.
    If environment variables are set, they override the configuration file. If neither are set, an exception is raised.

    Args:
        config_path: The path to the configuration file. Optional, defaults to `db.cfg` in the root of the module.

    Returns: The database configuration.
    Raises: ValueError if no configuration is available.
    """
    provider: Optional[DBConfigProvider] = None
    if _env_vars_available():
        logger.debug("Using environment variables for database configuration")
        provider = DBConfigProviderEnvVarBasedImpl()
    elif config_path is not None and config_path.exists():
        logger.debug(f"Using configuration file {config_path} for database configuration")
        provider = DBConfigProviderFileBasedImpl(config_path)

    if provider is None:
        msg = (
            f"No database configuration provider available. "
            f"Please either create a configuration file under {config_path} "
            f"or set the following environment variables: "
            f"{DBConfigProviderEnvVarBasedImpl.required_env_vars}"
        )
        logger.error(msg)
        raise ValueError(msg)

    return provider.get_config()


def get_database_url(config_path: Optional[Path] = DEFAULT_PATH) -> str:
    """
    Returns: The database URL.
    """
    db_config = get_db_config(config_path)
    logger.debug(f"Loaded database configuration: {db_config}")
    return _create_database_url_from_config(db_config)
