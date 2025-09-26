# Hebcal API Client

[![PyPI version](https://badge.fury.io/py/hebcal-api.svg)](https://badge.fury.io/py/hebcal-api)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/sudo-py-dev/hebcal-api/blob/main/LICENSE)

A comprehensive, async-first Python client for the [Hebcal Jewish Calendar API](https://www.hebcal.com/home/195/jewish-calendar-rest-api). This library provides easy access to Jewish calendar events, Shabbat times, Torah readings, and more.

## Features

- 🗓️ **Complete Calendar API** - Access all Jewish calendar events and holidays
- 🕯️ **Shabbat Times** - Get candle lighting and Havdalah times for any location
- 📖 **Torah Readings** - Retrieve weekly Torah portions and leyning information
- ⏰ **Zmanim** - Calculate daily Jewish prayer times and halachic times
- 🔄 **Date Conversion** - Convert between Hebrew and Gregorian dates
- 💀 **Yahrzeit** - Calculate Hebrew death anniversaries
- ⚡ **Async Support** - Full async/await support with httpx
- 🔄 **Sync Support** - Synchronous API with requests
- 📍 **Location Support** - Geonames, coordinates, ZIP codes, and city names
- 🌍 **International** - Support for multiple languages and locations worldwide

## Installation

```bash
pip install hebcal-api
```

Or install from source:

```bash
git clone https://github.com/sudo-py-dev/hebcal-api.git
cd hebcal-api
pip install -e .
```

## Quick Start

### Basic Calendar Usage

```python
from hebcal_api import Calendar

# Create a calendar instance
calendar = Calendar()

# Get events for a specific date range
events = calendar.get_events(
    start="2024-01-01",
    end="2024-01-31",
    geonameid=281184  # Jerusalem
)

for event in events.items:
    print(f"{event.date}: {event.title}")
```

### Shabbat Times

```python
from hebcal_api import Shabat

# Create a Shabbat instance
shabat = Shabat()

# Get Shabbat times for New York
times = shabat.get_shabbat(
    geonameid=5128581,  # New York City
    candle_lighting=True,
    leyning=True  # Include Torah reading
)

print(f"Candle lighting: {times.items[0].candle_lighting}")
print(f"Havdalah: {times.items[0].havdalah}")
print(f"Parasha: {times.items[0].parasha}")
```

### Async Usage

```python
import asyncio
from hebcal_api import Calendar

async def main():
    calendar = Calendar()

    # Get events asynchronously
    events = await calendar.get_events_async(
        year=2024,
        major_holidays=True,
        geonameid=281184
    )

    for event in events.items:
        print(f"{event.date}: {event.title}")

# Run the async function
asyncio.run(main())
```

## API Reference

### Calendar Class

The main class for accessing Jewish calendar events and holidays.

```python
from hebcal_api import Calendar

calendar = Calendar()

# Get events with various options
events = calendar.get_events(
    # Date parameters
    start="2024-01-01",           # Start date (YYYY-MM-DD)
    end="2024-12-31",            # End date (YYYY-MM-DD)
    year=2024,                   # Year (Gregorian or Hebrew)
    month=1,                     # Month (1-12 or 'x' for all)

    # Location (choose one)
    geonameid=281184,            # Geonames.org ID
    zip_code="10001",            # US ZIP code
    latitude=40.7128,            # Latitude
    longitude=-74.0060,          # Longitude
    city_name="New York",        # City name

    # Event types
    major_holidays=True,         # Major Jewish holidays
    minor_holidays=True,         # Minor holidays
    special_shabbatot=True,      # Special Shabbatot
    weekly_torah_portion=True,   # Parashat Hashavua
    candle_lighting_times=True,  # Candle lighting
    daf_yomi=True,               # Daily Talmud study

    # Other options
    israel_holidays_and_torah_readings=True,
    language="en"                # Language code
)
```

### Shabbat Class

Get Shabbat times and Torah readings for any location.

```python
from hebcal_api import Shabat

shabat = Shabat()

times = shabat.get_shabbat(
    # Location (required)
    geonameid=5128581,           # New York City
    # latitude=40.7128,          # Alternative: coordinates
    # longitude=-74.0060,

    # Times
    candle_lighting=True,        # Include candle lighting
    havdalah_at_nightfall=True,  # Use nightfall for Havdalah

    # Torah portion
    leyning=True,                # Include weekly reading

    # Timing adjustments
    candle_lighting_minutes_before_sunset=18,
    havdalah_minutes_after_sunset=42,

    # Language
    language="en"
)
```

### Zmanim Class

Calculate daily Jewish prayer times and halachic times.

```python
from hebcal_api import Zmanim

zmanim = Zmanim()

times = zmanim.get_zmanim(
    date="2024-01-15",
    geonameid=281184,            # Jerusalem
    # Or use coordinates:
    # latitude=31.7683,
    # longitude=35.2137,
    # timezone_id="Asia/Jerusalem"
)
```

### Date Converter

Convert between Hebrew and Gregorian dates.

```python
from hebcal_api import Converter

# Hebrew to Gregorian
gregorian = Converter.hdate_to_gdate(5784, 1, 15)  # 15 Shevat 5784
print(f"Hebrew date 15/1/5784 = {gregorian}")

# Gregorian to Hebrew
hebrew = Converter.gdate_to_hdate(2024, 1, 15)     # January 15, 2024
print(f"Gregorian date 2024-01-15 = {hebrew}")
```

### Yahrzeit

Calculate Hebrew death anniversaries.

```python
from hebcal_api import Yahrzeit

yahrzeit = Yahrzeit()

# Calculate Yahrzeit for a death date
anniversaries = yahrzeit.get_yahrzeit(
    death_date="2020-01-15",     # Gregorian death date
    year=2024,                   # Year to calculate for
    geonameid=5128581           # Location for Hebrew date
)
```

## Advanced Usage

### Custom Parameters

All methods accept additional parameters supported by the Hebcal API:

```python
from hebcal_api import Calendar

calendar = Calendar()

# Pass any Hebcal API parameter
events = calendar.get_events(
    year=2024,
    major_holidays=True,
    geonameid=281184,
    extra_params={
        "maj": "on",           # Major holidays
        "min": "on",           # Minor holidays
        "mod": "on",           # Modern holidays
        "i": "on",             # Israel-specific holidays
        "lg": "h"              # Hebrew language
    }
)
```

### Error Handling

```python
from hebcal_api import Calendar
from hebcal_api.tools.exception import FetchError

calendar = Calendar()

try:
    events = calendar.get_events(year=2024, geonameid=281184)
    print(f"Found {len(events.items)} events")
except FetchError as e:
    print(f"API Error: {e}")
except ValueError as e:
    print(f"Validation Error: {e}")
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/sudo-py-dev/hebcal-api.git
cd hebcal-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Code Quality

This project uses several tools to maintain code quality:

```bash
# Format code
black src/
isort src/

# Lint code
ruff check src/

# Type checking (if mypy is installed)
mypy src/
```

### Running Tests

```bash
# Run the test suite
python -m pytest

# Run with coverage
python -m pytest --cov=hebcal_api
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Follow PEP 8 style guidelines
2. Add type hints for all public functions
3. Include docstrings for all public classes and methods
4. Add tests for new functionality
5. Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## API Documentation

This library is a wrapper around the [Hebcal Jewish Calendar REST API](https://www.hebcal.com/home/195/jewish-calendar-rest-api). For complete API documentation, visit the official Hebcal API documentation.

## Support

If you encounter any issues or have questions:

- 📧 Email: sudopydev@gmail.com
- 🐛 [GitHub Issues](https://github.com/sudo-py-dev/hebcal-api/issues)
- 📖 [API Documentation](https://www.hebcal.com/home/195/jewish-calendar-rest-api)

## Changelog

### Version 0.1.2
- Initial release
- Complete API coverage for all Hebcal endpoints
- Async and sync support
- Sync support with requests
- Comprehensive type hints
- Full documentation and examples