"""
Hebcal Calendar API endpoint interface.
"""

from .client import HebcalClient
from .enums import Endpoint
from .models import CalendarRequest
from .utils.types import CalendarResponse


def fetch_calendar(request: CalendarRequest) -> CalendarResponse:
    """
    Fetch the main Jewish Calendar dates via synchronous execution.
    """
    return HebcalClient.execute(Endpoint.HEBCAL, request, CalendarResponse)


async def fetch_calendar_async(request: CalendarRequest) -> CalendarResponse:
    """
    Fetch the main Jewish Calendar dates via asynchronous execution.
    """
    return await HebcalClient.execute_async(Endpoint.HEBCAL, request, CalendarResponse)
