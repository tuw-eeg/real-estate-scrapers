"""Handles checking raw data format"""


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
