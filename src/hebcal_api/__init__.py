"""
Hebcal API - A comprehensive library for interacting with the Hebcal.com Jewish Calendar API.

This package provides both synchronous and asynchronous interfaces to fetch Jewish calendar
events, Shabbat times, Zmanim, torque readings, and date conversions.
"""

__version__ = "0.2.0"

from .calendar import fetch_calendar, fetch_calendar_async
from .client import HebcalClient
from .converter import fetch_converter, fetch_converter_async
from .enums import Endpoint, HebrewLanguage, YahrzeitEventType, YearType
from .exceptions import HebcalError, HebcalNetworkError, HebcalParseError, HebcalValidationError
from .leyning import fetch_leyning, fetch_leyning_async
from .models import (
    CalendarRequest,
    ConverterRequest,
    LeyningRequest,
    LocationConfig,
    ShabbatRequest,
    YahrzeitRequest,
    YahrzeitRequestEvent,
    ZmanimRequest,
)
from .shabat import fetch_shabbat, fetch_shabbat_async
from .utils.logger import logger
from .utils.types import (
    CalendarResponse,
    CandleInfo,
    ConverterResponse,
    Event,
    EventType,
    HavdalahInfo,
    HebrewDateParts,
    HolidayInfo,
    LeyningItem,
    LeyningResponse,
    Location,
    OmerInfo,
    ParashatInfo,
    RangeInfo,
    ReadingPortion,
    RoshChodeshInfo,
    ShabbatInfo,
    YahrzeitResponse,
    ZmanimEvent,
    ZmanimResponse,
    ZmanimTimes,
)
from .yahrzeit import fetch_yahrzeit, fetch_yahrzeit_async
from .zmanim import fetch_zmanim, fetch_zmanim_async

__all__ = [
    "CalendarRequest",
    "CalendarResponse",
    "CandleInfo",
    "ConverterRequest",
    "ConverterResponse",
    "Endpoint",
    "Event",
    "EventType",
    "HavdalahInfo",
    "HebcalClient",
    "HebcalError",
    "HebcalNetworkError",
    "HebcalParseError",
    "HebcalValidationError",
    "HebrewDateParts",
    "HebrewLanguage",
    "HolidayInfo",
    "LeyningItem",
    "LeyningRequest",
    "LeyningResponse",
    "Location",
    "LocationConfig",
    "OmerInfo",
    "ParashatInfo",
    "RangeInfo",
    "ReadingPortion",
    "RoshChodeshInfo",
    "ShabbatInfo",
    "ShabbatRequest",
    "YahrzeitEventType",
    "YahrzeitRequest",
    "YahrzeitRequestEvent",
    "YahrzeitResponse",
    "YearType",
    "ZmanimEvent",
    "ZmanimRequest",
    "ZmanimResponse",
    "ZmanimTimes",
    "fetch_calendar",
    "fetch_calendar_async",
    "fetch_converter",
    "fetch_converter_async",
    "fetch_leyning",
    "fetch_leyning_async",
    "fetch_shabbat",
    "fetch_shabbat_async",
    "fetch_yahrzeit",
    "fetch_yahrzeit_async",
    "fetch_zmanim",
    "fetch_zmanim_async",
    "logger",
]
