"""
Verify the Omer count for the current day (April 10, 2026).
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hebcal_api import CalendarRequest, fetch_calendar
from hebcal_api.utils.types import EventType


def test_omer_today():
    """Verify today's Omer count is correct and formatted."""
    # Today is April 10, 2026
    today_str = "2026-04-10"

    request = CalendarRequest(
        start=today_str,
        end=today_str,
        o=True,  # Enable Omer count
        maj=True,
        min=True,
    )

    response = fetch_calendar(request)

    print(f"\n--- Omer Count Test for {today_str} ---")

    omer_events = [item for item in response.items if item.type == EventType.OMER]

    if not omer_events:
        print("FAIL: No Omer event found for today!")
        sys.exit(1)

    event = omer_events[0]
    print(f"Title: {event.title}")
    print(f"Hebrew: {event.hebrew}")

    # Verification
    # April 10, 2026 is the 8th day of the Omer
    assert "8th day" in event.title.lower() or "omer 8" in event.title.lower() or "8" in event.title
    assert event.type == EventType.OMER

    print("\nSUCCESS: Omer count for today verified correctly.")


if __name__ == "__main__":
    test_omer_today()
