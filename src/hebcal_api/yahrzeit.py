"""
Yahrzeit and Anniversary API endpoint interface.
"""

from .client import HebcalClient
from .enums import Endpoint
from .models import YahrzeitRequest
from .utils.types import YahrzeitResponse


def fetch_yahrzeit(request: YahrzeitRequest) -> YahrzeitResponse:
    """
    Fetch Yahrzeit details via synchronous execution.
    """
    return HebcalClient.execute(Endpoint.YAHRZEIT, request, YahrzeitResponse)


async def fetch_yahrzeit_async(request: YahrzeitRequest) -> YahrzeitResponse:
    """
    Fetch Yahrzeit details via asynchronous execution.
    """
    return await HebcalClient.execute_async(Endpoint.YAHRZEIT, request, YahrzeitResponse)
