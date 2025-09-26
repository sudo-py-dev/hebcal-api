import httpx
import requests
from .exception import FetchError, InvalidGeoLocationError
from .logger import logger
import re


async def fetch_async(url: str, params: dict = None, timeout: int = 10, headers: dict = None):
    try:
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            full_url = response.url
            logger.debug(f"Fetched {full_url} successfully")
            return response.json()
    except httpx.HTTPStatusError as e:
        full_url = getattr(e.response, 'url', url) if e.response else url
        if e.response.status_code == 404:
            try:
                error_message = e.response.json().get("error", "Unknown error")
                if error_message and "can't find geonameid" in error_message:
                    raise InvalidGeoLocationError(error_message)
            except ValueError:
                error_message = "Unknown error"
            logger.error(f"HTTP status error fetching {full_url}: {e.response.status_code} - {error_message}")
            raise FetchError(f"HTTP status error fetching {full_url}: {e.response.status_code} - {error_message}") from e
        logger.error(f"HTTP status error fetching {full_url}: {e.response.status_code}")
        raise FetchError(f"HTTP status error fetching {full_url}: {e.response.status_code}") from e
    except httpx.RequestError as e:
        logger.error(f"Request error fetching {url}: {e}")
        raise FetchError(f"Request error fetching {url}: {e}")


def fetch_sync(url: str, params: dict = None, timeout: int = 10, headers: dict = None):
    try:
        response = requests.get(url, params=params, timeout=timeout, headers=headers)
        response.raise_for_status()
        full_url = response.url
        logger.debug(f"Fetched {full_url} successfully")
        return response.json()
    except requests.HTTPError as e:
        full_url = getattr(e.request, 'url', url) if e.request else url
        if e.response and e.response.status_code == 404:
            try:
                error_message = e.response.json().get("error", "Unknown error")
                if error_message and"can't find geonameid" in error_message:
                    raise InvalidGeoLocationError(error_message)
            except ValueError:
                error_message = "Unknown error"
            logger.error(f"HTTP status error fetching {full_url}: {e.response.status_code} - {error_message}")
            raise FetchError(f"HTTP status error fetching {full_url}: {e.response.status_code} - {error_message}") from e
        logger.error(f"HTTP status error fetching {full_url}: {e.response.status_code if e.response else 'Unknown'}")
        raise FetchError(f"HTTP status error fetching {full_url}: {e.response.status_code if e.response else 'Unknown'}") from e
    except (requests.RequestException, requests.ConnectionError, requests.ConnectTimeout) as e:
        logger.error(f"Request error fetching {url}: {e}")
        raise FetchError(f"Request error fetching {url}: {e}")


def remove_hebrew_nikud(text: str) -> str:
    """
    Remove Hebrew vowel points (nikud) from a string.

    Raises:
        ValueError: If text is None.
    """
    if not text:
        raise ValueError("Input text cannot be None")

    # Unicode range for Hebrew diacritics: 0x0591–0x05C7
    return re.sub(r'[\u0591-\u05C7]', '', text)
