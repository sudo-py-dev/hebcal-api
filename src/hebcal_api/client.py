"""
Unified execution engine for Hebcal API requests.
"""

from typing import TypeVar

from .enums import Endpoint
from .models import (
    CalendarRequest,
    ConverterRequest,
    LeyningRequest,
    ShabbatRequest,
    YahrzeitRequest,
    ZmanimRequest,
)
from .utils.logger import logger
from .utils.utils import fetch_async, fetch_sync

T = TypeVar("T")

# Unified type for all request objects
HebcalRequest = (
    CalendarRequest
    | ShabbatRequest
    | ZmanimRequest
    | LeyningRequest
    | ConverterRequest
    | YahrzeitRequest
)


class HebcalClient:
    """
    Unified client for executing requests against the Hebcal API.

    This class abstracts the common logic for preparing parameters and handling
    network execution for both synchronous and asynchronous operations.
    """

    @staticmethod
    def execute(endpoint: Endpoint, request_obj: HebcalRequest, response_class: type[T]) -> T:
        """
        Execute a synchronous request.

        Args:
            endpoint: The API endpoint (e.g. hebcal, shabbat, etc.)
            request_obj: A validated Pydantic model representing the request.
            response_class: The data class to instantiate with the response.

        Returns:
            An instance of response_class populated with API data.
        """
        url = f"https://www.hebcal.com/{endpoint.value}"
        params = request_obj.to_api_params()

        logger.debug(f"Fetching {endpoint.value} from {url} with params {params}")
        data = fetch_sync(url, params=params)

        if hasattr(response_class, "from_api"):
            return response_class.from_api(data, url=url, params=params)  # type: ignore
        if hasattr(response_class, "from_dict"):
            return response_class.from_dict(data, url=url, params=params)  # type: ignore

        return response_class(data, url=url, params=params)  # type: ignore

    @staticmethod
    async def execute_async(
        endpoint: Endpoint, request_obj: HebcalRequest, response_class: type[T]
    ) -> T:
        """
        Execute an asynchronous request.

        Args:
            endpoint: The API endpoint.
            request_obj: A validated Pydantic model representing the request.
            response_class: The data class to instantiate.

        Returns:
            An instance of response_class populated with API data.
        """
        url = f"https://www.hebcal.com/{endpoint.value}"
        params = request_obj.to_api_params()

        logger.debug(f"Fetching async {endpoint.value} from {url} with params {params}")
        data = await fetch_async(url, params=params)

        if hasattr(response_class, "from_api"):
            return response_class.from_api(data, url=url, params=params)  # type: ignore
        if hasattr(response_class, "from_dict"):
            return response_class.from_dict(data, url=url, params=params)  # type: ignore

        return response_class(data, url=url, params=params)  # type: ignore
