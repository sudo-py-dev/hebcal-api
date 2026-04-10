# Hebcal API Client

[![PyPI version](https://badge.fury.io/py/hebcal-api.svg)](https://badge.fury.io/py/hebcal-api)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/sudo-py-dev/hebcal-api/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A comprehensive, production-grade Python client for the [Hebcal Jewish Calendar API](https://www.hebcal.com/home/195/jewish-calendar-rest-api). Modernized with **Pydantic v2**, **httpx**, and **strict type safety**.

## Features

- 🗓️ **Functional API** - Clean, functional interface for all Hebcal endpoints.
- ✅ **Pydantic Validation** - Type-safe request models with automatic parameter validation.
- 🇮🇱 **Clean Hebrew Output** - Specialized formatters that prioritize clean, nikud-free Hebrew text.
- 🕯️ **Advanced Shabbat & Zmanim** - Precise halachic times for any location worldwide.
- 🌾 **Omer Support** - Full support for fetching and formatting the daily Omer count.
- ⚡ **Async Native** - Built on `httpx` for high-performance asynchronous operations.
- 📍 **Flattened Location Support** - Direct use of Geonames, coordinates, or city names.

## Installation

```bash
pip install hebcal-api
```

Or with `uv`:

```bash
uv add hebcal-api
```

## Quick Start

### Basic Calendar Usage
Get Jewish holidays and events for any location.

```python
from hebcal_api import CalendarRequest, fetch_calendar
from hebcal_api.utils.calendar_formatter import format_calendar_events

# Create a request for Jerusalem
request = CalendarRequest(
    location="Jerusalem",
    geonameid=281184,
    maj=True,    # Major holidays
    min=True     # Minor holidays
)

# Fetch data synchronously
response = fetch_calendar(request)

# Format for display (Always clean Hebrew by default)
print(format_calendar_events(response))
```

### Shabbat Times
Fetch candle lighting and Havdalah times.

```python
from hebcal_api import ShabbatRequest, fetch_shabbat

request = ShabbatRequest(
    geonameid=5128581,  # New York City
    c=True,             # Candle lighting
    s=True              # Shabbat info
)

response = fetch_shabbat(request)

for event in response.items:
    print(f"{event.title}: {event.date}")
```

### Omer Count Today
Easily track the daily Omer count.

```python
from hebcal_api import CalendarRequest, fetch_calendar

request = CalendarRequest(o=True)  # Enable Omer count
response = fetch_calendar(request)

# Find the Omer event
omer_event = next((i for i in response.items if i.type == "omer"), None)
if omer_event:
    print(f"Today is: {omer_event.title}")
```

### Async Usage
Full async support for integration into modern web frameworks.

```python
import asyncio
from hebcal_api import CalendarRequest, fetch_calendar_async

async def main():
    request = CalendarRequest(geonameid=281184)
    response = await fetch_calendar_async(request)
    
    for event in response.items:
        print(f"{event.title} - {event.hebrew}")

asyncio.run(main())
```

## API Reference

### Functional Interface
The library provides high-level `fetch_*` functions for both sync and async execution:

| Endpoint | Sync Function | Async Function |
| :--- | :--- | :--- |
| `/hebcal` | `fetch_calendar` | `fetch_calendar_async` |
| `/shabbat` | `fetch_shabbat` | `fetch_shabbat_async` |
| `/zmanim` | `fetch_zmanim` | `fetch_zmanim_async` |
| `/converter` | `fetch_converter` | `fetch_converter_async` |
| `/yahrzeit` | `fetch_yahrzeit` | `fetch_yahrzeit_async` |
| `/leyning` | `fetch_leyning` | `fetch_leyning_async` |

### Unified Client
For custom network configuration, use the `HebcalClient`:

```python
from hebcal_api import HebcalClient

# Configure custom timeout or headers
response = HebcalClient.execute(
    endpoint=Endpoint.CALENDAR,
    request=request,
    response_model=CalendarResponse,
    timeout=30
)
```

## Error Handling

The library uses a hierarchy of specific exceptions:

- `HebcalError`: Base exception for all library errors.
- `HebcalNetworkError`: Raised for HTTP connection or status code failures.
- `HebcalValidationError`: Raised when request parameters are invalid (e.g., missing location).
- `HebcalParseError`: Raised when the API response cannot be parsed into the expected models.

## Formatting Utilities
Located in `hebcal_api.utils.calendar_formatter`, these helper functions turn raw data into professional messages.

- `format_calendar_events(response)`: Returns a beautiful, multi-line string of events.
- `remove_hebrew_nikud(text)`: Manually strip diacritics from any Hebrew string.

## Development

Set up the project using `uv`:

```bash
git clone https://github.com/sudo-py-dev/hebcal-api.git
cd hebcal-api
uv sync
```

### Code Quality
We enforce strict linting and type checking:

```bash
uv run ruff check      # Linting
uv run ruff format     # Formatting
uv run pyright src/    # Type safety
uv run pytest          # Testing
```

## License
MIT License. See [LICENSE](LICENSE) for details.

## Support
- 📧 Email: sudopydev@gmail.com
- 🐛 [GitHub Issues](https://github.com/sudo-py-dev/hebcal-api/issues)
- 📖 [Official API Documentation](https://www.hebcal.com/home/195/jewish-calendar-rest-api)