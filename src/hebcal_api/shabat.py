"""
Shabbat times API endpoint interface.
"""

from .client import HebcalClient
from .enums import Endpoint
from .models import ShabbatRequest
from .utils.types import CalendarResponse


def fetch_shabbat(request: ShabbatRequest) -> CalendarResponse:
    """
    Fetch Shabbat times via synchronous execution.
    """
    return HebcalClient.execute(Endpoint.SHABBAT, request, CalendarResponse)


async def fetch_shabbat_async(request: ShabbatRequest) -> CalendarResponse:
    """
    Fetch Shabbat times via asynchronous execution.
    """
    return await HebcalClient.execute_async(Endpoint.SHABBAT, request, CalendarResponse)
