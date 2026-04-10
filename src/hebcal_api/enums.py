"""
Enumerations for Hebcal API parameters and endpoints.
"""

from enum import StrEnum


class Endpoint(StrEnum):
    """Supported Hebcal API endpoints."""

    HEBCAL = "hebcal"
    SHABBAT = "shabbat"
    ZMANIM = "zmanim"
    LEYNING = "leyning"
    CONVERTER = "converter"
    YAHRZEIT = "yahrzeit"


class HebrewLanguage(StrEnum):
    """Supported languages and transliteration schemes."""

    ENGLISH = "en"
    HEBREW = "he"
    HEBREW_NO_NIKUD = "he-x-NoNikud"
    ASHKENAZI = "a"


class YearType(StrEnum):
    """Types of years supported by Hebcal (Gregorian vs Hebrew)."""

    GREGORIAN = "G"
    HEBREW = "H"


class YahrzeitEventType(StrEnum):
    """Types of events supported by the Yahrzeit API."""

    YAHRZEIT = "Yahrzeit"
    BIRTHDAY = "Birthday"
    ANNIVERSARY = "Anniversary"
