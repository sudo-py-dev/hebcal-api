"""
Shared networking and string processing utilities.
"""

import re
from typing import Any

import httpx

from hebcal_api.exceptions import HebcalNetworkError, HebcalValidationError


async def fetch_async(
    url: str,
    params: dict[str, Any] | None = None,
    timeout: int = 10,
    headers: dict[str, str] | None = None,
) -> Any:  # noqa: ANN401
    """Execute an asynchronous GET request."""
    try:
        async with httpx.AsyncClient(
            timeout=timeout, headers=headers, follow_redirects=True
        ) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_message = e.response.text or str(e)
        if e.response.status_code == 404 and "can't find geonameid" in error_message.lower():
            raise HebcalValidationError(error_message) from e

        raise HebcalNetworkError(
            f"API request failed: {error_message}", status_code=e.response.status_code
        ) from e
    except Exception as e:
        raise HebcalNetworkError(f"Unexpected network error: {e}") from e


def fetch_sync(
    url: str,
    params: dict[str, Any] | None = None,
    timeout: int = 10,
    headers: dict[str, str] | None = None,
) -> Any:  # noqa: ANN401
    """Execute a synchronous GET request."""
    try:
        with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_message = e.response.text or str(e)
        if e.response.status_code == 404 and "can't find geonameid" in error_message.lower():
            raise HebcalValidationError(error_message) from e

        raise HebcalNetworkError(
            f"API request failed: {error_message}", status_code=e.response.status_code
        ) from e
    except Exception as e:
        raise HebcalNetworkError(f"Unexpected network error: {e}") from e


def remove_hebrew_nikud(text: str) -> str:
    """
    Remove Niqqud (vowels) and other diacritics from Hebrew text.
    """
    if not text:
        raise HebcalValidationError("Input text cannot be None or empty")

    # Unicode range for Hebrew diacritics: 0x0591-0x05C7
    return re.sub(r"[\u0591-\u05C7]", "", text)
