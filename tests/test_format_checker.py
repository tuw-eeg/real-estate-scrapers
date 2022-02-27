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


@pytest.mark.parametrize(
    "string,expected",
    [
        ("1900", True),
        ("2000", True),
        ("ca. 1903", True),
        ("Ca. 1963", True),
        ("Ca. ", False),
        (". ", False),
        ("", False),
        (" ", False),
    ],
)
def test_contains_number(string: str, expected: bool) -> None:
    assert FormatChecker.contains_number(string) == expected


@pytest.mark.parametrize(
    "string,expected",
    [
        ("1900", 1900),
        ("2000", 2000),
        ("ca. 1903", 1903),
        ("Ca. 1963", 1963),
    ],
)
def test_extract_year(string: str, expected: int) -> None:
    assert FormatChecker.extract_year(string) == expected


@pytest.mark.parametrize(
    "string",
    [
        "a",
        "",
        "NA",
        "-",
    ],
)
def test_extract_year_raises_error(string: str) -> None:
    with pytest.raises(ValueError):
        FormatChecker.extract_year(string)
