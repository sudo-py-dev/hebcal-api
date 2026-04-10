"""
Test script for the Hebrew Calendar Formatter
"""

import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hebcal_api.utils.calendar_formatter import (
    format_calendar_events,
    format_hebrew_calendar,
    get_holidays,
    get_shabbat_events,
    get_upcoming_events,
)
from hebcal_api.utils.types import (
    CalendarResponse,
)


def create_test_events():
    """Create a set of test events for the calendar"""
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Create events for different days
    return [
        # Today's events
        {
            "title": "הדלקת נרות",
            "date": (base_date.replace(hour=16, minute=30)).isoformat() + "+02:00",
            "category": "candles",
            "memo": "שבת שלום",
        },
        {
            "title": "פרשת השבוע",
            "date": base_date.isoformat(),
            "category": "parashat",
            "hebrew": "פרשת נח",
            "leyning": {
                "torah": "בראשית ו:ט-יא:לב",
                "haftarah": "ישעיהו נד:א-נד:יז",
                "maftir": "במדבר כח:ט-טו",
            },
        },
        # Tomorrow's events
        {
            "title": "הבדלה",
            "date": (base_date + timedelta(days=1)).replace(hour=17, minute=45).isoformat()
            + "+02:00",
            "category": "havdalah",
            "memo": "מוצ״ש",
        },
        # Rosh Chodesh next week
        {
            "title": "ראש חודש",
            "date": (base_date + timedelta(days=7)).isoformat(),
            "category": "roshchodesh",
            "hebrew": "ראש חודש חשוון",
            "memo": "חשוון",
            "leyning": {
                "torah": "במדבר כח:א-טו",
                "haftarah": "ישעיהו סו:א-כד",
                "1": "במדבר כח:א-ג",
                "2": "במדבר כח:ד-ה",
                "3": "במדבר כח:ו-י",
                "4": "במדבר כח:יא-טו",
            },
        },
        # Holiday next month
        {
            "title": "חנוכה",
            "date": (base_date + timedelta(days=30)).isoformat(),
            "category": "holiday",
            "hebrew": "חנוכה",
            "memo": "נר ראשון",
            "yomtov": True,
            "subcat": "major",
        },
        # Omer count
        {
            "title": "ספירת העומר",
            "date": (base_date + timedelta(days=120)).isoformat(),
            "category": "omer",
            "omer": {
                "count": {"en": "33", "he": "ל״ג"},
                "sefira": {"he": "ל״ג בעומר", "translit": "Lag BaOmer", "en": "Lag BaOmer"},
            },
        },
    ]


def test_calendar_formatter():
    """Test the calendar formatter with various events"""
    # Create test events
    mock_items = create_test_events()

    # Create a mock response
    mock_data = {
        "items": mock_items,
        "title": "לוח שנה עברי",
        "date": datetime.now().isoformat(),
        "location": {"title": "ישראל", "tzid": "Asia/Jerusalem"},
    }

    mock_response = CalendarResponse(mock_data)

    # Test full calendar formatting
    result = format_hebrew_calendar(mock_response)
    assert "הדלקת נרות" in result
    assert "פרשת נח" in result

    # Test getting holidays
    holidays = get_holidays(mock_response)
    assert len(holidays) >= 1
    assert any("חנוכה" in h.title for h in holidays)

    # Test getting Shabbat events
    shabbat_events = get_shabbat_events(mock_response)
    assert len(shabbat_events) >= 1

    # Test getting upcoming events
    upcoming = get_upcoming_events(mock_response, days=14)
    assert len(upcoming) >= 1

    # Test with empty response
    empty_response = CalendarResponse({"items": []})
    empty_result = format_calendar_events(empty_response)
    assert "אין אירועים" in empty_result


if __name__ == "__main__":
    mock_items = create_test_events()
    mock_data = {
        "items": mock_items,
        "title": "לוח שנה עברי",
        "date": datetime.now().isoformat(),
        "location": {"title": "ישראל", "tzid": "Asia/Jerusalem"},
    }
    mock_response = CalendarResponse(mock_data)
    formatted_text = format_hebrew_calendar(mock_response)

    print("\n--- Formatted Hebrew Calendar ---\n")
    print(formatted_text)
    print("\n--- End of Output ---\n")
