"""
Utility functions for formatting Hebcal API responses into human-readable strings.
"""

from datetime import datetime, timedelta
from typing import Any

from .types import CalendarResponse, Event, EventType
from .utils import remove_hebrew_nikud


def format_time(dt: datetime | None) -> str:
    """Format datetime to a readable time string."""
    if not dt:
        return ""
    return dt.strftime("%H:%M")


def format_hebrew_date(hebrew_date: str | None) -> str:
    """Format Hebrew date string to be more readable."""
    if not hebrew_date:
        return ""
    return remove_hebrew_nikud(hebrew_date)


def format_candle_lighting(event: Event) -> str:
    """Format candle lighting event."""
    if not event.candle:
        return ""

    time_str = format_time(event.candle.time)
    if event.holiday and event.holiday.yomtov:
        return f"🕯️ הדלקת נרות (חג): {time_str}"
    return f"🕯️ הדלקת נרות: {time_str}"


def format_havdalah(event: Event) -> str:
    """Format havdalah event."""
    if not event.havdalah:
        return ""

    time_str = format_time(event.havdalah.time)
    if event.holiday and event.holiday.yomtov:
        return f"✨ הבדלה (חג): {time_str}"
    return f"✨ הבדלה: {time_str}"


def format_parashat(event: Event) -> str:
    """Format parashat hashavua."""
    if not event.parashat:
        return ""

    parts: list[str] = []
    if event.parashat.torah:
        parts.append(f"תורה: {remove_hebrew_nikud(event.parashat.torah)}")
    if event.parashat.haftarah:
        parts.append(f"הפטרה: {remove_hebrew_nikud(event.parashat.haftarah)}")

    title = remove_hebrew_nikud(event.hebrew if event.hebrew else event.title)
    if not parts:
        return f"📖 {title}"

    return f"📖 {title} ({', '.join(parts)})"


def format_rosh_chodesh(event: Event) -> str:
    """Format rosh chodesh."""
    if not event.roshchodesh:
        return ""

    parts: list[str] = []
    if event.roshchodesh.torah:
        parts.append(f"קריאת התורה: {remove_hebrew_nikud(event.roshchodesh.torah)}")
    if event.roshchodesh.haftarah:
        parts.append(f"הפטרה: {remove_hebrew_nikud(event.roshchodesh.haftarah)}")

    title = remove_hebrew_nikud(event.hebrew if event.hebrew else event.title)
    if not parts:
        return f"🌒 {title}"

    return f"🌒 {title} ({'; '.join(parts)})"


def format_holiday(event: Event) -> str:
    """Format holiday event."""
    if not event.holiday:
        return ""

    emoji = "🎉"
    title_en = event.title.lower()
    if "פסח" in event.title or "pesach" in title_en:
        emoji = "🍷"
    elif "סוכות" in event.title or "sucot" in title_en or "שמחת תורה" in event.title:
        emoji = "🌿"
    elif "ראש השנה" in event.title or "hashana" in title_en:
        emoji = "🍏🍯"
    elif "יום כיפור" in event.title or "kippur" in title_en:
        emoji = "🕍"

    title = remove_hebrew_nikud(event.hebrew if event.hebrew else event.title)
    return f"{emoji} {title}"


def format_omer(event: Event) -> str:
    """Format omer count."""
    if not event.omer:
        return ""

    count = remove_hebrew_nikud(event.omer.count_he)
    sefira = remove_hebrew_nikud(event.omer.sefira_he)
    return f"🌾 ספירת העומר: {count} - {sefira}"


def format_event(event: Event) -> str:
    """Format a single calendar event based on its type."""
    if event.type == EventType.CANDLES:
        return format_candle_lighting(event)
    elif event.type == EventType.HAVDALAH:
        return format_havdalah(event)
    elif event.type == EventType.PARASHAT:
        return format_parashat(event)
    elif event.type == EventType.ROSH_CHODESH:
        return format_rosh_chodesh(event)
    elif event.type == EventType.HOLIDAY:
        return format_holiday(event)
    elif event.type == EventType.OMER:
        return format_omer(event)

    title = remove_hebrew_nikud(event.hebrew if event.hebrew else event.title)
    if event.type == EventType.DAF_YOMI:
        return f"📚 דף יומי: {title}"

    return f"📅 {title}"


def format_calendar_events(response: CalendarResponse) -> str:
    """
    Format calendar events into a human-readable string.
    Always prioritizes Hebrew text without nikud.

    Args:
        response: CalendarResponse object containing events

    Returns:
        Formatted string with calendar events
    """
    if not response or not response.items:
        return "אין אירועים ליום זה"  # No events for today

    # Group events by date
    events_by_date: dict[str, list[Event]] = {}
    for event in response.items:
        if not event.date:
            continue
        date_key = event.date.strftime("%Y-%m-%d")
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    # Format each day's events
    result: list[str] = []
    for date_key in sorted(events_by_date.keys()):
        date_events = events_by_date[date_key]
        date_str = date_events[0].date.strftime("%d/%m/%Y") if date_events[0].date else ""
        result.append(f"\n📅 <b>{date_str}</b>")

        # Sort events by type (prioritize Parashat) and then by time
        def get_event_sort_key(e: Event) -> tuple[int, Any, str]:
            # Assign priority to Parashat events (they come first)
            type_priority = 0 if e.type == EventType.PARASHAT else 1
            event_dt = e.date
            time_value = event_dt.time() if event_dt else datetime.max.time()
            return (type_priority, time_value, str(e.type))

        sorted_events = sorted(date_events, key=get_event_sort_key)

        # Format each event
        for event in sorted_events:
            formatted = format_event(event)
            if formatted:
                result.append(f"• {formatted}")

    return "\n".join(result) if result else "אין אירועים ליום זה"


def format_hebrew_calendar(response: CalendarResponse) -> str:
    """
    Format calendar events specifically for Hebrew-speaking users.
    Always prioritizes Hebrew text without nikud.
    """
    return format_calendar_events(response)


def get_upcoming_events(response: CalendarResponse, days: int = 7) -> list[Event]:
    """
    Get upcoming events within the specified number of days.

    Args:
        response: CalendarResponse object containing events
        days: Number of days to look ahead

    Returns:
        List of upcoming events
    """
    if not response or not response.items:
        return []

    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    return [
        event for event in response.items if event.date and today <= event.date.date() <= end_date
    ]


def get_holidays(response: CalendarResponse) -> list[Event]:
    """Get all holiday events from the response."""
    if not response or not response.items:
        return []
    return [e for e in response.items if e.type == EventType.HOLIDAY]


def get_shabbat_events(response: CalendarResponse) -> list[Event]:
    """Get all Shabbat-related events from the response."""
    if not response or not response.items:
        return []
    return [
        e
        for e in response.items
        if e.type in (EventType.CANDLES, EventType.HAVDALAH, EventType.SHABBAT)
    ]
