"""
Hebrew-Gregorian date conversion interface.
"""

from typing import Any, cast

from .config import BASE_URL
from .enums import Endpoint
from .models import ConverterRequest
from .utils.types import ConverterResponse
from .utils.utils import fetch_async, fetch_sync


def fetch_converter(request: ConverterRequest) -> list[ConverterResponse]:
    """
    Fetch converted dates via synchronous execution.

    Note: Always returns a List of ConverterResponses because range conversions
    natively return lists in the API.

    Args:
        request: A ConverterRequest model specifying dates and conversion direction.
    """
    params_for_api = request.to_api_params()

    url = f"{BASE_URL}/{Endpoint.CONVERTER.value}"
    raw_data: Any = fetch_sync(url, params=params_for_api)
    if isinstance(raw_data, list):
        return [
            ConverterResponse.from_api(cast("dict[str, Any]", item), url=url, params=params_for_api)
            for item in cast("list[Any]", raw_data)
        ]
    return [
        ConverterResponse.from_api(cast("dict[str, Any]", raw_data), url=url, params=params_for_api)
    ]


async def fetch_converter_async(request: ConverterRequest) -> list[ConverterResponse]:
    """
    Fetch converted dates via asynchronous execution.

    Args:
        request: A ConverterRequest model specifying dates and conversion direction.
    """
    params_for_api = request.to_api_params()

    url = f"{BASE_URL}/{Endpoint.CONVERTER.value}"
    raw_data: Any = await fetch_async(url, params=params_for_api)
    if isinstance(raw_data, list):
        return [
            ConverterResponse.from_api(cast("dict[str, Any]", item), url=url, params=params_for_api)
            for item in cast("list[Any]", raw_data)
        ]
    return [
        ConverterResponse.from_api(cast("dict[str, Any]", raw_data), url=url, params=params_for_api)
    ]
