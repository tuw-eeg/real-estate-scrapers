"""Loads the database configuration from the config file."""
import configparser
from pathlib import Path
from typing import NamedTuple

config_path = Path(__file__).parent.parent.parent / "db.cfg"
assert config_path.exists()


def _get_config_object() -> configparser.ConfigParser:
    """
    Loads a configuration file into a `configparser.ConfigParser`
    object based on the specified file path.

    Returns: the `configparser.ConfigParser` object
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


class DBConfig(NamedTuple):
    """
    A typed dictionary that contains the database configuration.
    """

    database: str
    host: str
    port: int
    user: str
    password: str


def get_db_config() -> DBConfig:
    """
    Loads the database configuration from the config file.

    Returns: the database configuration
    """
    config = _get_config_object()
    return DBConfig(
        database=config.get("connection", "database"),
        host=config.get("connection", "host"),
        port=int(config.get("connection", "port")),
        user=config.get("credentials", "user"),
        password=config.get("credentials", "password"),
    )


def _create_database_url_from_config(cfg: DBConfig) -> str:
    """
    Args:
        cfg: The database configuration.

    Returns: The database URL.
    """
    return f"postgresql://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}"


def get_database_url() -> str:
    """
    Returns: The database URL.
    """
    return _create_database_url_from_config(get_db_config())
