"""
Quick-access helper functions for common Hebcal API operations.
"""

from datetime import date, datetime

from .calendar import fetch_calendar
from .models import CalendarRequest
from .utils.types import CalendarResponse


def fetch_holidays(
    year: int, location: str | None = None, major_only: bool = False
) -> CalendarResponse:
    """
    Get holidays for a given year.

    Args:
        year: The Gregorian or Hebrew year (e.g. 2024 or 5784).
        location: Optional city name.
        major_only: If True, only fetch major holidays.
    """
    req = CalendarRequest(
        year=year,
        city=location,
        maj=major_only,
    )
    return fetch_calendar(req)


def fetch_shabbat_times(
    start_date: str | date | datetime,
    end_date: str | date | datetime,
    location: str,
    candle_lighting: bool = True,
) -> CalendarResponse:
    """
    Get Shabbat candle lighting and Havdalah times for a date range.

    Args:
        start_date: Starting date (YYYY-MM-DD or date/datetime object).
        end_date: Ending date.
        location: City name for location-based times.
        candle_lighting: If True, include candle lighting times.
    """
    req = CalendarRequest(
        start=start_date,
        end=end_date,
        city=location,
        c=candle_lighting,
    )
    return fetch_calendar(req)


def fetch_daf_yomi(dt: str | date | datetime | None = None) -> CalendarResponse:
    """
    Get Daf Yomi for a specific date or today.

    Args:
        dt: Optional date to lookup. Defaults to today's date if None.
    """
    req = CalendarRequest(F=True)
    if dt:
        if isinstance(dt, (datetime, date)):
            req.start = req.end = dt.strftime("%Y-%m-%d")
        else:
            req.start = req.end = dt

    return fetch_calendar(req)
