"""
Leyning (Torah reading) API endpoint interface.
"""

from .client import HebcalClient
from .enums import Endpoint
from .models import LeyningRequest
from .utils.types import LeyningResponse


def fetch_leyning(request: LeyningRequest) -> LeyningResponse:
    """
    Fetch Torah reading (Leyning) via synchronous execution.
    """
    return HebcalClient.execute(Endpoint.LEYNING, request, LeyningResponse)


async def fetch_leyning_async(request: LeyningRequest) -> LeyningResponse:
    """
    Fetch Torah reading (Leyning) via asynchronous execution.
    """
    return await HebcalClient.execute_async(Endpoint.LEYNING, request, LeyningResponse)
