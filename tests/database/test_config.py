"""Database config tests."""
import re

from real_estate_scrapers.database.config import get_database_url, get_db_config


def test_config_loads() -> None:
    assert get_db_config() is not None


def test_database_url_is_valid() -> None:
    url = get_database_url()
    assert url is not None
    assert (
        re.match(r"^postgresql://[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@[a-zA-Z0-9_\-\.]+:[0-9]+/[a-zA-Z0-9_\-]+$", url)
        is not None
    )
