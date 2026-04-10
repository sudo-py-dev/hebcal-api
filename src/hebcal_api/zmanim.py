"""
Zmanim (Halachic times) API endpoint interface.
"""

from .client import HebcalClient
from .enums import Endpoint
from .models import ZmanimRequest
from .utils.types import ZmanimResponse


def fetch_zmanim(request: ZmanimRequest) -> ZmanimResponse:
    """
    Fetch Halachic timings via synchronous execution.
    """
    return HebcalClient.execute(Endpoint.ZMANIM, request, ZmanimResponse)


async def fetch_zmanim_async(request: ZmanimRequest) -> ZmanimResponse:
    """
    Fetch Halachic timings via asynchronous execution.
    """
    return await HebcalClient.execute_async(Endpoint.ZMANIM, request, ZmanimResponse)
