"""Database config tests."""
import re
from os import environ

from real_estate_scrapers.database.config import get_database_url, get_db_config


def test_config_loads_from_file() -> None:
    assert get_db_config() is not None


def test_config_loads_from_env() -> None:
    required_env_vars = (
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )
    values = ("test", "localhost", "5432", "test", "test")
    # Setup
    for key, value in zip(required_env_vars, values):
        environ[key] = value

    # Test
    db_config = get_db_config()
    assert db_config is not None

    url = get_database_url()
    assert url is not None
    assert _db_url_is_valid(url)
    assert url == "postgresql://test:test@localhost:5432/test"

    # Teardown
    for key in required_env_vars:
        del environ[key]


def test_database_url_is_valid() -> None:
    url = get_database_url()
    assert url is not None
    assert _db_url_is_valid(url)


def _db_url_is_valid(url: str) -> bool:
    return (
        re.match(r"^postgresql://[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@[a-zA-Z0-9_\-\.]+:[0-9]+/[a-zA-Z0-9_\-]+$", url)
        is not None
    )
