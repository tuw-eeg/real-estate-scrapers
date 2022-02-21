"""``FormatChecker`` unit tests."""

import pytest

from real_estate_scrapers.format_checker import FormatChecker


@pytest.mark.parametrize(
    "string,expected",
    [
        ("-1", True),
        ("-1.12", True),
        ("0", True),
        ("1", True),
        ("1.123", True),
        ("1,123", False),
        ("some text", False),
    ],
)
def test_is_numeric(string: str, expected: bool) -> None:
    assert FormatChecker.is_numeric(string) == expected
