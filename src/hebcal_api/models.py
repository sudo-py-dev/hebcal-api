"""
Pydantic Request models for Hebcal API endpoints.
"""

from datetime import date as dt_date
from datetime import datetime as dt_datetime
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hebcal_api.enums import HebrewLanguage, YearType


class BaseRequest(BaseModel):
    """Base configuration for Pydantic models."""

    model_config = ConfigDict(extra="ignore", use_enum_values=True)


class LocationConfig(BaseRequest):
    """Shared location configuration for multiple endpoints."""

    geonameid: int | None = None
    city: str | None = None
    zip: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tzid: str | None = None


class CalendarRequest(BaseRequest):
    """Request parameters for the /hebcal endpoint."""

    v: str = "1"
    cfg: str = "json"
    maj: bool = True
    min: bool = True
    nx: bool = True
    mf: bool = True
    ss: bool = True
    mod: bool = True
    lg: HebrewLanguage = HebrewLanguage.ENGLISH
    year: str | int = "now"
    yt: YearType = YearType.GREGORIAN
    month: str | int = "x"
    start: dt_date | dt_datetime | str | None = None
    end: dt_date | dt_datetime | str | None = None
    city: str | None = None
    geonameid: int | None = None
    zip: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tzid: str | None = None
    c: bool = False  # Candle lighting
    m: int | None = None  # Havdalah
    b: int | None = None  # Candles
    F: bool = False  # Daf Yomi
    o: bool = False  # Omer count

    @model_validator(mode="after")
    def validate_year_month(self) -> "CalendarRequest":
        """Validate year and month compatibility."""
        if str(self.year) != "now":
            try:
                int(self.year)
            except ValueError as err:
                raise ValueError("year must be 'now' or an integer") from err

        if str(self.month) != "x":
            try:
                m = int(self.month)
                if not (1 <= m <= 12):
                    raise ValueError()
            except ValueError as err:
                raise ValueError("month must be 'x' or 1-12") from err

        return self

    def to_api_params(self) -> dict[str, Any]:
        """Convert model to API query parameters."""
        params = self.model_dump(exclude_none=True)
        # Convert booleans to 'on' or 'off'
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = "on" if value else "off"
        return params


class ShabbatRequest(BaseRequest):
    """Request parameters for the /shabbat endpoint."""

    cfg: str = "json"
    v: str = "1"
    geo: str = "geoname"
    geonameid: int | None = None
    city: str | None = None
    zip: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tzid: str | None = None
    m: int = 42  # Havdalah minutes past sunset
    b: int = 18  # Candle lighting minutes before sunset

    @model_validator(mode="after")
    def validate_location(self) -> "ShabbatRequest":
        """Ensure valid location parameters are provided."""
        if self.geonameid:
            self.geo = "geoname"
        elif self.city:
            self.geo = "city"
        elif self.zip:
            self.geo = "zip"
        elif self.latitude is not None and self.longitude is not None:
            self.geo = "pos"
        else:
            raise ValueError("Must provide geonameid, city, zip, or coordinates")
        return self

    def to_api_params(self) -> dict[str, Any]:
        """Convert model to API query parameters."""
        return self.model_dump(exclude_none=True)


class ZmanimRequest(BaseRequest):
    """Request parameters for the /zmanim endpoint."""

    cfg: str = "json"
    geo: str = "geoname"
    geonameid: int | None = None
    zip: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tzid: str | None = None
    date: dt_date | dt_datetime | str | None = None
    start: dt_date | dt_datetime | str | None = None
    end: dt_date | dt_datetime | str | None = None
    sec: bool = False
    elevation: int | None = None

    @model_validator(mode="after")
    def validate_params(self) -> "ZmanimRequest":
        """Validate location and date parameters."""
        # Location validation
        if self.geonameid:
            self.geo = "geoname"
        elif self.city:
            self.geo = "city"
        elif self.zip:
            self.geo = "zip"
        elif self.latitude is not None and self.longitude is not None:
            self.geo = "pos"
        else:
            raise ValueError("Must provide geonameid, city, zip, or coordinates")

        # Date validation
        if self.date is not None and (self.start or self.end):
            raise ValueError("Cannot specify both 'date' and 'start/end'.")
        return self

    def to_api_params(self) -> dict[str, Any]:
        """Convert model to API query parameters."""
        params: dict[str, Any] = self.model_dump(
            exclude={"date", "start", "end"}, exclude_none=True
        )

        def format_dt(dt: dt_date | dt_datetime | str | None) -> str:
            if not dt:
                return ""
            if isinstance(dt, (dt_date, dt_datetime)):
                return dt.strftime("%Y-%m-%d")
            return str(dt)

        if self.date:
            params["date"] = format_dt(self.date)
        if self.start and self.end:
            params["start"] = format_dt(self.start)
            params["end"] = format_dt(self.end)

        if self.sec:
            params["sec"] = "1"
        if self.elevation:
            params["ue"] = "on"
        return params


class LeyningRequest(BaseRequest):
    """Request parameters for the /leyning endpoint."""

    date: dt_date | dt_datetime | str | None = None
    start: dt_date | dt_datetime | str | None = None
    end: dt_date | dt_datetime | str | None = None
    diaspora: bool = False
    triennial: bool = True

    @model_validator(mode="after")
    def validate_dates(self) -> "LeyningRequest":
        """Ensure date range or specific date is provided."""
        if self.date is not None and (self.start or self.end):
            raise ValueError("Cannot specify both 'date' and 'start/end'.")
        if self.date is None and not (self.start and self.end):
            raise ValueError("Provide either 'date' or both 'start' and 'end'.")
        return self

    def to_api_params(self) -> dict[str, Any]:
        """Convert model to API query parameters."""
        params: dict[str, Any] = {"cfg": "json"}

        def format_dt(dt: dt_date | dt_datetime | str | None) -> str:
            if not dt:
                return ""
            if isinstance(dt, (dt_date, dt_datetime)):
                return dt.strftime("%Y-%m-%d")
            return str(dt)

        if self.date:
            params["date"] = format_dt(self.date)
        elif self.start and self.end:
            params["start"] = format_dt(self.start)
            params["end"] = format_dt(self.end)

        params["i"] = "on" if self.diaspora else "off"
        params["tri"] = "1" if self.triennial else "0"
        return params


class ConverterRequest(BaseRequest):
    """Request parameters for the /converter endpoint."""

    cfg: str = "json"
    gd: int | None = None
    gm: int | None = None
    gy: int | None = None
    hd: int | None = None
    hm: str | None = None
    hy: int | None = None
    date: dt_date | dt_datetime | str | None = None
    h2g: bool | None = None
    gs: bool = False  # Hebrew date with Sephardic transliteration

    @model_validator(mode="after")
    def validate_params(self) -> "ConverterRequest":
        """Ensure either Gregorian or Hebrew parameters are provided."""
        has_g = all(v is not None for v in [self.gd, self.gm, self.gy]) or self.date
        has_h = all(v is not None for v in [self.hd, self.hm, self.hy])

        if not (has_g or has_h):
            raise ValueError("Must provide Gregorian date info or Hebrew date info")

        if self.h2g is None:
            self.h2g = has_h

        return self

    def to_api_params(self) -> dict[str, Any]:
        """Convert model to API query parameters."""
        params = self.model_dump(exclude={"date"}, exclude_none=True)

        if self.date:
            dt = self.date
            if isinstance(dt, (dt_date, dt_datetime)):
                params["date"] = dt.strftime("%Y-%m-%d")
            else:
                params["date"] = str(dt)

        params["h2g"] = "1" if self.h2g else "0"
        params["gs"] = "on" if self.gs else "off"
        return params


class YahrzeitRequestEvent(BaseRequest):
    """Sub-model for an individual yahrzeit event in a request."""

    type: Literal["Y", "A", "B", "M"] = "Y"
    day: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int
    name: str = "Event"
    sunset: bool = False


class YahrzeitRequest(BaseRequest):
    """Request parameters for the /yahrzeit endpoint."""

    cfg: str = "json"
    events: list[YahrzeitRequestEvent] = Field(default_factory=list)
    years: int = 1

    def to_api_params(self) -> dict[str, Any]:
        """Convert model to API query parameters."""
        params: dict[str, Any] = {"cfg": "json", "years": self.years}
        events_list = cast("list[YahrzeitRequestEvent]", self.events)
        for i, event in enumerate(events_list, 1):
            params[f"t{i}"] = event.type
            params[f"d{i}"] = event.day
            params[f"m{i}"] = event.month
            params[f"y{i}"] = event.year
            params[f"n{i}"] = event.name
            if event.sunset:
                params[f"s{i}"] = "on"
        return params
