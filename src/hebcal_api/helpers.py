"""
Helper functions for easier access to common Hebcal API queries
"""

from typing import Optional, Dict, Any, Union
from datetime import date, datetime
from .calendar import Calendar
from .tools.types import CalendarResponse


def get_holidays(
    year: int,
    location: Optional[str] = None,
    major_only: bool = False
) -> CalendarResponse:
    """
    Get Jewish holidays for a specific year.

    Args:
        year: Gregorian year
        location: City name or geonameid
        major_only: If True, only return major holidays

    Example:
        holidays = get_holidays(2024, "New York")
    """
    calendar = Calendar()
    params = {"year": year, "maj": "on"}

    if major_only:
        params["min"] = "off"
        params["mf"] = "off"

    if location:
        params["city"] = location

    return calendar._get_calendar_sync(params)


def get_shabbat_times(
    start_date: Union[str, date, datetime],
    end_date: Union[str, date, datetime],
    location: str,
    candle_lighting: bool = True
) -> CalendarResponse:
    """
    Get Shabbat times for a date range.

    Args:
        start_date: Start date
        end_date: End date
        location: City name
        candle_lighting: Include candle lighting times

    Example:
        shabbat = get_shabbat_times("2024-01-01", "2024-12-31", "Jerusalem")
    """
    calendar = Calendar()
    params = {
        "start": calendar._format_datetime(start_date),
        "end": calendar._format_datetime(end_date),
        "city": location,
        "c": "on" if candle_lighting else "off"
    }

    return calendar._get_calendar_sync(params)


def get_daf_yomi(date: Optional[Union[str, date, datetime]] = None) -> CalendarResponse:
    """
    Get Daf Yomi for a specific date or today.

    Args:
        date: Date to get Daf Yomi for (defaults to today)

    Example:
        daf = get_daf_yomi("2024-01-15")
    """
    calendar = Calendar()
    params = {"F": "on"}

    if date:
        params["start"] = calendar._format_datetime(date)
        params["end"] = calendar._format_datetime(date)

    return calendar._get_calendar_sync(params)
