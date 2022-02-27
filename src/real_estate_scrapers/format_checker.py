"""Handles checking raw data format"""
import re


class FormatChecker:
    """Handles checking raw data format"""

    @staticmethod
    def is_numeric(string: str) -> bool:
        """
        Args:
            string: string to check

        Returns:
            True if string is numeric, False otherwise
        """
        try:
            float(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def contains_number(string: str) -> bool:
        """
        Args:
            string: string to check

        Returns:
            True if string contains number, False otherwise
        """
        return bool(re.search(r"\d", string))

    @staticmethod
    def extract_year(string: str) -> int:
        """
        Args:
            string: string to extract year from

        Returns:
            year extracted from string
        """
        match = re.search(r"\d+", string)
        if match is None:
            raise ValueError(f"Could not extract year from string: {string}")
        return int(match.group())
