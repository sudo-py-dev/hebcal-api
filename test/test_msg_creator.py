#!/usr/bin/env python3
"""
Test script for the Hebrew Calendar Formatter
"""
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hebcal_api.tools.calendar_formatter import (
    format_calendar_events,
    format_hebrew_calendar,
    get_holidays,
    get_shabbat_events,
    get_upcoming_events
)
from hebcal_api.tools.types import (
    CalendarResponse, 
    Event, 
    CandleInfo, 
    HavdalahInfo, 
    HolidayInfo, 
    ParashatInfo, 
    RoshChodeshInfo,
    OmerInfo
)
from datetime import datetime

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
            "memo": "שבת שלום"
        },
        {
            "title": "פרשת השבוע",
            "date": base_date.isoformat(),
            "category": "parashat",
            "hebrew": "פרשת נח",
            "leyning": {
                "torah": "בראשית ו:ט-יא:לב",
                "haftarah": "ישעיהו נד:א-נד:יז",
                "maftir": "במדבר כח:ט-טו"
            }
        },
        # Tomorrow's events
        {
            "title": "הבדלה",
            "date": (base_date + timedelta(days=1)).replace(hour=17, minute=45).isoformat() + "+02:00",
            "category": "havdalah",
            "memo": "מוצ״ש"
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
                "4": "במדבר כח:יא-טו"
            }
        },
        # Holiday next month
        {
            "title": "חנוכה",
            "date": (base_date + timedelta(days=30)).isoformat(),
            "category": "holiday",
            "hebrew": "חנוכה",
            "memo": "נר ראשון",
            "yomtov": True,
            "subcat": "major"
        },
        # Omer count
        {
            "title": "ספירת העומר",
            "date": (base_date + timedelta(days=120)).isoformat(),
            "category": "omer",
            "omer": {
                "count": {"en": "33", "he": "ל״ג"},
                "sefira": {
                    "he": "ל״ג בעומר",
                    "translit": "Lag BaOmer",
                    "en": "Lag BaOmer"
                }
            }
        }
    ]

def test_calendar_formatter():
    """Test the calendar formatter with various events"""
    print("\n🔄 Testing Hebrew Calendar Formatter...\n")

    # Create test events
    mock_items = create_test_events()
    
    # Create a mock response
    mock_data = {
        'items': mock_items,
        'title': 'לוח שנה עברי',
        'date': datetime.now().isoformat(),
        'location': {'title': 'ישראל', 'tzid': 'Asia/Jerusalem'}
    }

    mock_response = CalendarResponse(mock_data)

    try:
        # Test full calendar formatting
        print("📅 Testing full calendar formatting...")
        result = format_hebrew_calendar(mock_response)
        print("✅ Format successful!")
        print("\n" + "="*50)
        print("📜 לוח שנה עברי")
        print("="*50)
        print(result)
        print("="*50 + "\n")

        # Test getting holidays
        print("\n🎉 Testing holiday extraction...")
        holidays = get_holidays(mock_response)
        print(f"Found {len(holidays)} holiday(s):")
        for holiday in holidays:
            print(f"- {holiday.title} ({holiday.date.strftime('%d/%m/%Y') if holiday.date else 'No date'})")

        # Test getting Shabbat events
        print("\n🕯️ Testing Shabbat events...")
        shabbat_events = get_shabbat_events(mock_response)
        print(f"Found {len(shabbat_events)} Shabbat-related event(s):")
        for event in shabbat_events:
            time_str = event.date.strftime('%H:%M') if event.date else 'All day'
            print(f"- {event.title} at {time_str}")

        # Test getting upcoming events
        print("\n⏳ Testing upcoming events (next 14 days)...")
        upcoming = get_upcoming_events(mock_response, days=14)
        print(f"Found {len(upcoming)} upcoming event(s):")
        for event in upcoming:
            date_str = event.date.strftime('%a, %d/%m/%Y %H:%M') if event.date else 'No specific time'
            print(f"- {event.title}: {date_str}")

        # Test with empty response
        print("\n🔍 Testing empty response...")
        empty_response = CalendarResponse({'items': []})
        empty_result = format_calendar_events(empty_response)
        print(f"Empty response result: {repr(empty_result)}")

        return True

    except Exception as e:
        print(f"\n❌ Error testing function: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("📆 Hebrew Calendar Formatter Tester")
    print("="*50)
    
    success = test_calendar_formatter()
    
    print("\n" + "="*50)
    print("✅ Tests completed successfully!" if success else "❌ Some tests failed!")
    print("="*50)
    
    sys.exit(0 if success else 1)
