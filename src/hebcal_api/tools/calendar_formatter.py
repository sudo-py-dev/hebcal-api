from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .types import CalendarResponse, Event, EventType


def format_time(dt: datetime) -> str:
    """Format datetime to a readable time string."""
    if not dt:
        return ""
    return dt.strftime("%H:%M")


def format_hebrew_date(hebrew_date: str) -> str:
    """Format Hebrew date string to be more readable."""
    if not hebrew_date:
        return ""
    # Add more sophisticated Hebrew date formatting if needed
    return hebrew_date


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
    
    parts = []
    if event.parashat.torah:
        parts.append(f"תורה: {event.parashat.torah}")
    if event.parashat.haftarah:
        parts.append(f"הפטרה: {event.parashat.haftarah}")
    
    if not parts:
        return f"📖 {event.title}"
    
    return f"📖 {event.title} ({', '.join(parts)})"


def format_rosh_chodesh(event: Event) -> str:
    """Format rosh chodesh."""
    if not event.roshchodesh:
        return ""
    
    parts = []
    if event.roshchodesh.torah:
        parts.append(f"קריאת התורה: {event.roshchodesh.torah}")
    if event.roshchodesh.haftarah:
        parts.append(f"הפטרה: {event.roshchodesh.haftarah}")
    
    if not parts:
        return f"🌒 {event.title}"
    
    return f"🌒 {event.title} ({'; '.join(parts)})"


def format_holiday(event: Event) -> str:
    """Format holiday event."""
    if not event.holiday:
        return ""
    
    emoji = "🎉"  # Default holiday emoji
    if "פסח" in event.title:
        emoji = "🍷"
    elif "סוכות" in event.title or "שמחת תורה" in event.title:
        emoji = "🌿"
    elif "ראש השנה" in event.title:
        emoji = "🍏🍯"
    elif "יום כיפור" in event.title:
        emoji = "🕍"
    
    return f"{emoji} {event.title}"


def format_omer(event: Event) -> str:
    """Format omer count."""
    if not event.omer:
        return ""
    
    return f"🌾 ספירת העומר: {event.omer.count_he} - {event.omer.sefira_he}"


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
    
    # Default formatting for unknown event types
    return f"📅 {event.title}"


def format_calendar_events(response: CalendarResponse, include_hebrew: bool = True) -> str:
    """
    Format calendar events into a human-readable string.
    
    Args:
        response: CalendarResponse object containing events
        include_hebrew: Whether to include Hebrew text
        
    Returns:
        Formatted string with calendar events
    """
    if not response or not response.items:
        return "אין אירועים ליום זה"  # No events for today
    
    # Group events by date
    events_by_date = {}
    for event in response.items:
        if not event.date:
            continue
        date_key = event.date.strftime("%Y-%m-%d")
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)
    
    # Format each day's events
    result = []
    for date_key in sorted(events_by_date.keys()):
        date_events = events_by_date[date_key]
        date_str = date_events[0].date.strftime("%d/%m/%Y")
        result.append(f"\n📅 *{date_str}*")
        
        # Sort events by time (if available) or by type
        def get_event_sort_key(e):
            if e.date:
                return (e.date.time(), str(e.type))
            return (datetime.max.time(), str(e.type))
            
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
    This is an alias for format_calendar_events with Hebrew enabled by default.
    """
    return format_calendar_events(response, include_hebrew=True)


def get_upcoming_events(response: CalendarResponse, days: int = 7) -> List[Event]:
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
        event for event in response.items
        if event.date and today <= event.date.date() <= end_date
    ]


def get_holidays(response: CalendarResponse) -> List[Event]:
    """Get all holiday events from the response."""
    if not response or not response.items:
        return []
    return [e for e in response.items if e.type == EventType.HOLIDAY]


def get_shabbat_events(response: CalendarResponse) -> List[Event]:
    """Get all Shabbat-related events from the response."""
    if not response or not response.items:
        return []
    return [e for e in response.items if e.type in (EventType.CANDLES, EventType.HAVDALAH, EventType.SHABBAT)]