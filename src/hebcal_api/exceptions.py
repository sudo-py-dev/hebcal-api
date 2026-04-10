"""
Custom exceptions for the Hebcal API library.
"""


class HebcalError(Exception):
    """Base exception for all Hebcal API errors."""

    pass


class HebcalNetworkError(HebcalError):
    """Raised when an API request fails due to network issues."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class HebcalValidationError(HebcalError):
    """Raised when request parameters fail validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class HebcalParseError(HebcalError):
    """Failed to parse or interpret data from the Hebcal API."""

    pass
