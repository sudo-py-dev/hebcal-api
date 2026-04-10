"""
Data models representing Hebcal API responses.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, cast


class EventType(StrEnum):
    """
    Enumeration of possible event types in the Jewish calendar.

    Attributes
    ----------
    OMER : str
        Represents a day of the Omer count.
    HOLIDAY : str
        Represents a Jewish holiday or festival.
    HAVDALAH : str
        Represents Havdalah (end-of-Shabbat ceremony).
    CANDLES : str
        Represents candle lighting times.
    ROSH_CHODESH : str
        Represents the beginning of a new Hebrew month.
    SHABBAT : str
        Represents Shabbat events or times.
    PARASHAT : str
        Represents the weekly Torah portion.
    ZMANIM : str
        Represents daily halachic times (zmanim) such as sunrise, sunset, etc.
    UNKNOWN : str
        Represents an event type that could not be classified.
    """

    OMER = "omer"
    HOLIDAY = "holiday"
    HAVDALAH = "havdalah"
    CANDLES = "candles"
    ROSH_CHODESH = "roshchodesh"
    SHABBAT = "shabbat"
    PARASHAT = "parashat"
    ZMANIM = "zmanim"
    DAF_YOMI = "dafyomi"
    UNKNOWN = "unknown"


@dataclass
class Location:
    title: str
    city: str
    tzid: str
    latitude: float
    longitude: float
    cc: str
    country: str
    elevation: int | None = None
    admin1: str | None = None
    asciiname: str | None = None
    geo: str | None = None
    geonameid: int | None = None


@dataclass
class OmerInfo:
    count_he: str
    count_en: str
    sefira_he: str
    sefira_translit: str
    sefira_en: str

    sefira_en: str


@dataclass
class HolidayInfo:
    yomtov: bool | None = None
    subcategory: str | None = None
    memo: str | None = None
    leyning: dict[str, Any] | None = None


@dataclass
class RangeInfo:
    start: datetime
    end: datetime


@dataclass
class HavdalahInfo:
    time: datetime | None = None
    memo: str | None = None


@dataclass
class CandleInfo:
    time: datetime | None = None
    memo: str | None = None


@dataclass
class ShabbatInfo:
    torah: str | None = None
    haftarah: str | None = None
    maftir: str | None = None
    leyning: dict[str, Any] | None = None


@dataclass
class RoshChodeshInfo:
    link: str | None = None
    torah: str | None = None
    haftarah: str | None = None
    maftir: str | None = None
    portions: dict[str, str] | None = None  # For the '1', '2', etc.
    memo: str | None = None


@dataclass
class ZmanimEvent:
    title: str  # e.g. "תְּחִילַּת הַצוֹם"
    date: datetime  # datetime object with tzinfo
    type: EventType = EventType.ZMANIM
    hebrew: str | None = None  # Hebrew string (e.g. "תחילת הצום")
    original_title: str | None = None  # English/Original title
    memo: str | None = None  # extra info (e.g. "צוֹם גְּדַלְיָה")
    subcat: str | None = None  # sub-category ("fast", "sunrise", etc.)

    subcat: str | None = None  # sub-category ("fast", "sunrise", etc.)


@dataclass
class ParashatInfo:
    torah: str | None = None
    haftarah: str | None = None
    maftir: str | None = None
    aliyot: dict[str, str] | None = None
    triennial: dict[str, str] | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ParashatInfo":
        if not data:
            return ParashatInfo()
        aliyot = {k: v for k, v in data.items() if k.isdigit()}
        return ParashatInfo(
            torah=data.get("torah"),
            haftarah=data.get("haftarah"),
            maftir=data.get("maftir"),
            aliyot=aliyot if aliyot else None,
            triennial=data.get("triennial"),
        )


@dataclass
class Event:
    title: str
    date: datetime | None = None
    type: EventType = EventType.UNKNOWN
    hebrew: str | None = None
    link: str | None = None
    original_title: str | None = None
    omer: OmerInfo | None = None
    zmanim: ZmanimEvent | None = None
    holiday: HolidayInfo | None = None
    parashat: ParashatInfo | None = None
    havdalah: HavdalahInfo | None = None
    candle: CandleInfo | None = None
    shabbat: ShabbatInfo | None = None
    roshchodesh: RoshChodeshInfo | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Event":
        # Parse Omer info
        omer_info = None
        if "omer" in data:
            omer_info = OmerInfo(
                count_he=data["omer"]["count"].get("he", ""),
                count_en=data["omer"]["count"].get("en", ""),
                sefira_he=data["omer"]["sefira"].get("he", ""),
                sefira_translit=data["omer"]["sefira"].get("translit", ""),
                sefira_en=data["omer"]["sefira"].get("en", ""),
            )

        # Parse Holiday info
        holiday_info = None
        if data.get("category") == "holiday":
            holiday_info = HolidayInfo(
                yomtov=data.get("yomtov", False),
                subcategory=data.get("subcat"),
                memo=data.get("memo"),
                leyning=data.get("leyning"),
            )

        # Parse Shabbat / Parashat info
        parashat_info = None
        if data.get("category") == "parashat":
            parashat_info = ParashatInfo.from_dict(data.get("leyning", {}))

        shabbat_info = None
        if data.get("category") == "shabbat":
            leyning = data.get("leyning", {})
            shabbat_info = ShabbatInfo(
                torah=leyning.get("torah"),
                haftarah=leyning.get("haftarah"),
                maftir=leyning.get("maftir"),
                leyning=leyning,
            )

        zmanim_info = None
        if data.get("category") == "zmanim":
            zman_title = data.get("title", "")
            zman_date_str = data.get("date", "")
            zmanim_info = ZmanimEvent(
                title=zman_title,
                date=datetime.fromisoformat(zman_date_str) if zman_date_str else datetime.now(),
                type=EventType.ZMANIM,
                hebrew=data.get("hebrew"),
                original_title=data.get("title_orig"),
                memo=data.get("memo"),
                subcat=data.get("subcat"),
            )

        # Parse Havdalah info
        havdalah_info = None
        if data.get("category") == "havdalah":
            h_date_str = data.get("date", "")
            havdalah_info = HavdalahInfo(
                time=datetime.fromisoformat(h_date_str) if h_date_str else None,
                memo=data.get("memo"),
            )

        # Parse Candle info
        candle_info = None
        if data.get("category") == "candles":
            c_date_str = data.get("date", "")
            candle_info = CandleInfo(
                time=datetime.fromisoformat(c_date_str) if c_date_str else None,
                memo=data.get("memo"),
            )

        # Parse Shabbat / Parashat info (overwrite if leyning exists)
        if data.get("category") in ("shabbat", "parashat") or "leyning" in data:
            leyning = data.get("leyning", {})
            shabbat_info = ShabbatInfo(
                torah=leyning.get("torah"),
                haftarah=leyning.get("haftarah"),
                maftir=leyning.get("maftir"),
                leyning=leyning,
            )

        # Parse Rosh Chodesh info
        roshchodesh_info = None
        if data.get("category") in ("roshchodesh", "rosh chodesh"):
            leyning = data.get("leyning", {})
            roshchodesh_info = RoshChodeshInfo(
                link=data.get("link"),
                torah=leyning.get("torah"),
                haftarah=leyning.get("haftarah"),
                maftir=leyning.get("maftir"),
                portions={k: v for k, v in leyning.items() if k.isdigit()},
                memo=data.get("memo"),
            )

        # Parse date safely
        event_date = None
        if "date" in data:
            d_str = data["date"]
            if isinstance(d_str, str):
                try:
                    event_date = datetime.fromisoformat(d_str.replace("Z", "+00:00"))
                except Exception:
                    try:
                        event_date = datetime.strptime(d_str, "%Y-%m-%d")
                    except Exception:
                        event_date = None

        # Determine EventType safely
        category = str(data.get("category", "")).lower()
        event_type = (
            EventType(category) if category in EventType._value2member_map_ else EventType.UNKNOWN
        )

        return Event(
            title=data.get("title", ""),
            date=event_date,
            type=event_type,
            hebrew=data.get("hebrew"),
            link=data.get("link"),
            original_title=data.get("title_orig"),
            omer=omer_info,
            zmanim=zmanim_info,
            holiday=holiday_info,
            havdalah=havdalah_info,
            parashat=parashat_info,
            candle=candle_info,
            shabbat=shabbat_info,
            roshchodesh=roshchodesh_info,
        )


class CalendarResponse:
    def __init__(
        self, data: dict[str, Any], url: str | None = None, params: dict[str, Any] | None = None
    ) -> None:
        self._data = data
        self._url = url
        self._params = params

    @property
    def title(self) -> str:
        return self._data.get("title", "")

    @property
    def date(self) -> datetime:
        d_str = self._data.get("date", "")
        return datetime.fromisoformat(d_str) if d_str else datetime.now()

    @property
    def version(self) -> str:
        return self._data.get("version", "")

    @property
    def location(self) -> Location:
        loc = self._data.get("location", {})
        return Location(
            title=loc.get("title", ""),
            city=loc.get("city", ""),
            tzid=loc.get("tzid", ""),
            latitude=loc.get("latitude", 0.0),
            longitude=loc.get("longitude", 0.0),
            cc=loc.get("cc", ""),
            country=loc.get("country", ""),
            elevation=loc.get("elevation"),
            admin1=loc.get("admin1"),
            asciiname=loc.get("asciiname"),
            geo=loc.get("geo"),
            geonameid=loc.get("geonameid"),
        )

    @property
    def range(self) -> RangeInfo | None:
        r_data = self._data.get("range")
        if r_data:
            start_str = r_data.get("start", "")
            end_str = r_data.get("end", "")
            if start_str and end_str:
                return RangeInfo(
                    start=datetime.fromisoformat(start_str),
                    end=datetime.fromisoformat(end_str),
                )
        return None

    @property
    def items(self) -> list[Event]:
        raw_items = self._data.get("items", [])
        return [Event.from_dict(item) for item in raw_items]

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def query(self) -> str | None:
        if self._url and self._params:
            from urllib.parse import urlencode

            param_str = urlencode(self._params)
            return f"{self._url}?{param_str}"
        return None


@dataclass
class ReadingPortion:
    k: str  # book
    b: str  # begin
    e: str  # end
    v: int | None = None
    p: int | None = None
    note: str | None = None


@dataclass
class LeyningItem:
    date: datetime
    hdate: str
    type: str
    name_en: str
    name_he: str
    parsha_num: int | None = None
    summary: str | None = None
    summary_parts: list[dict[str, str]] | None = None
    fullkriyah: dict[str, ReadingPortion] | None = None
    haftara: str | None = None
    haft: ReadingPortion | None = None
    tri_year: int | None = None
    tri_haftara: str | None = None
    tri_haft: ReadingPortion | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LeyningItem":
        def parse_portion(d: dict[str, Any] | None) -> dict[str, ReadingPortion]:
            if not d:
                return {}
            return {k: ReadingPortion(**v) for k, v in d.items()}

        return LeyningItem(
            date=datetime.fromisoformat(data["date"]),
            hdate=data.get("hdate", ""),
            type=data.get("type", ""),
            name_en=data.get("name", {}).get("en", ""),
            name_he=data.get("name", {}).get("he", ""),
            parsha_num=data.get("parshaNum"),
            summary=data.get("summary"),
            summary_parts=data.get("summaryParts"),
            fullkriyah=parse_portion(data.get("fullkriyah")),
            haftara=data.get("haftara"),
            haft=ReadingPortion(**data["haft"]) if data.get("haft") else None,
            tri_year=data.get("triYear"),
            tri_haftara=data.get("triHaftara"),
            tri_haft=ReadingPortion(**data["triHaft"]) if data.get("triHaft") else None,
        )

    tri_haft: ReadingPortion | None = None


@dataclass
class LeyningResponse:
    date: datetime
    location: str
    range_start: str
    range_end: str
    items: list[LeyningItem]
    _data: dict[str, Any] | None = None  # Store raw data
    _url: str | None = None  # Store query URL
    _params: dict[str, Any] | None = None  # Store query params

    @staticmethod
    def from_dict(
        data: dict[str, Any], url: str | None = None, params: dict[str, Any] | None = None
    ) -> "LeyningResponse":
        return LeyningResponse(
            date=datetime.fromisoformat(data["date"]),
            location=data.get("location", ""),
            range_start=data.get("range", {}).get("start", ""),
            range_end=data.get("range", {}).get("end", ""),
            items=[LeyningItem.from_dict(item) for item in data.get("items", [])],
            _data=data,
            _url=url,
            _params=params,
        )

    @property
    def raw(self) -> dict[str, Any]:
        return self._data or {}

    @property
    def query(self) -> str | None:
        if self._url and self._params:
            from urllib.parse import urlencode

            param_str = urlencode(self._params)
            return f"{self._url}?{param_str}"
        return None


@dataclass
class ZmanimTimes:
    chatzot_night: str | None = None
    alot_ha_shachar: str | None = None
    misheyakir: str | None = None
    misheyakir_machmir: str | None = None
    dawn: str | None = None
    sunrise: str | None = None
    sea_level_sunrise: str | None = None
    sof_zman_shma_mga_19_8: str | None = None
    sof_zman_shma_mga_16_1: str | None = None
    sof_zman_shma_mga: str | None = None
    sof_zman_shma: str | None = None
    sof_zman_tfilla_mga_19_8: str | None = None
    sof_zman_tfilla_mga_16_1: str | None = None
    sof_zman_tfilla_mga: str | None = None
    sof_zman_tfilla: str | None = None
    chatzot: str | None = None
    mincha_gedola: str | None = None
    mincha_gedola_mga: str | None = None
    mincha_ketana: str | None = None
    mincha_ketana_mga: str | None = None
    plag_ha_mincha: str | None = None
    sea_level_sunset: str | None = None
    sunset: str | None = None
    bein_ha_shmashos: str | None = None
    dusk: str | None = None
    tzeit_7_083deg: str | None = None
    tzeit_8_5deg: str | None = None
    tzeit_42min: str | None = None
    tzeit_50min: str | None = None
    tzeit_72min: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ZmanimTimes":
        mapping = {
            "chatzot_night": data.get("chatzotNight"),
            "alot_ha_shachar": data.get("alotHaShachar"),
            "misheyakir": data.get("misheyakir"),
            "misheyakir_machmir": data.get("misheyakirMachmir"),
            "dawn": data.get("dawn"),
            "sunrise": data.get("sunrise"),
            "sea_level_sunrise": data.get("seaLevelSunrise"),
            "sof_zman_shma_mga_19_8": data.get("sofZmanShmaMGA19Point8"),
            "sof_zman_shma_mga_16_1": data.get("sofZmanShmaMGA16Point1"),
            "sof_zman_shma_mga": data.get("sofZmanShmaMGA"),
            "sof_zman_shma": data.get("sofZmanShma"),
            "sof_zman_tfilla_mga_19_8": data.get("sofZmanTfillaMGA19Point8"),
            "sof_zman_tfilla_mga_16_1": data.get("sofZmanTfillaMGA16Point1"),
            "sof_zman_tfilla_mga": data.get("sofZmanTfillaMGA"),
            "sof_zman_tfilla": data.get("sofZmanTfilla"),
            "chatzot": data.get("chatzot"),
            "mincha_gedola": data.get("minchaGedola"),
            "mincha_gedola_mga": data.get("minchaGedolaMGA"),
            "mincha_ketana": data.get("minchaKetana"),
            "mincha_ketana_mga": data.get("minchaKetanaMGA"),
            "plag_ha_mincha": data.get("plagHaMincha"),
            "sea_level_sunset": data.get("seaLevelSunset"),
            "sunset": data.get("sunset"),
            "bein_ha_shmashos": data.get("beinHaShmashos"),
            "dusk": data.get("dusk"),
            "tzeit_7_083deg": data.get("tzeit7083deg"),
            "tzeit_8_5deg": data.get("tzeit85deg"),
            "tzeit_42min": data.get("tzeit42min"),
            "tzeit_50min": data.get("tzeit50min"),
            "tzeit_72min": data.get("tzeit72min"),
        }
        return cls(**mapping)


@dataclass
class ZmanimResponse:
    date: Any
    version: str
    location: Any
    times: ZmanimTimes
    _data: dict[str, Any] | None = None  # Store raw data
    _url: str | None = None  # Store query URL
    _params: dict[str, Any] | None = None  # Store query params

    @classmethod
    def from_api(
        cls, data: dict[str, Any], url: str | None = None, params: dict[str, Any] | None = None
    ) -> "ZmanimResponse":
        times_data = data.get("times", {})
        times_obj = ZmanimTimes.from_dict(times_data)
        return cls(
            date=data["date"],
            version=data["version"],
            location=data["location"],
            times=times_obj,
            _data=data,
            _url=url,
            _params=params,
        )

    @property
    def raw(self) -> dict[str, Any]:
        return self._data or {}

    @property
    def query(self) -> str | None:
        if self._url and self._params:
            from urllib.parse import urlencode

            param_str = urlencode(self._params)
            return f"{self._url}?{param_str}"
        return None


@dataclass
class HebrewDateParts:
    yy: int
    mm: int
    dd: int
    month_name: str

    @staticmethod
    def from_api(data: dict[str, Any]) -> "HebrewDateParts":
        return HebrewDateParts(
            yy=int(data.get("yy", 0)),
            mm=int(data.get("mm", 0)),
            dd=int(data.get("dd", 0)),
            month_name=str(data.get("month_name", "")),
        )


@dataclass
class YahrzeitEvent:
    title: str
    date: datetime | None = None
    hebrew: str | None = None
    category: str = ""
    anniversary: int | None = None
    yahrzeit_of: str | None = None
    he_date_parts: HebrewDateParts | None = None

    @staticmethod
    def from_api(data: dict[str, Any]) -> "YahrzeitEvent":
        date_str = data.get("date")
        parsed_date = None
        if date_str:
            try:
                parsed_date = datetime.fromisoformat(str(date_str))
            except (ValueError, TypeError):
                parsed_date = None

        y_title = str(data.get("title", ""))
        y_cat = str(data.get("category", ""))
        return YahrzeitEvent(
            title=y_title,
            date=parsed_date,
            hebrew=data.get("hebrew"),
            category=y_cat,
            anniversary=data.get("anniversary"),
            yahrzeit_of=data.get("yahrzeitOf"),
            he_date_parts=HebrewDateParts.from_api(data["heDateParts"])
            if "heDateParts" in data
            else None,
        )


@dataclass
class YahrzeitResponse:
    events: list[YahrzeitEvent]
    _data: dict[str, Any] | None = None  # Store raw data
    _url: str | None = None  # Store query URL
    _params: dict[str, Any] | None = None  # Store query params

    @staticmethod
    def from_api(
        data: dict[str, Any], url: str | None = None, params: dict[str, Any] | None = None
    ) -> "YahrzeitResponse":
        # The API returns a dict with 'events' key containing the list
        events_data = data.get("events", [])
        if isinstance(events_data, str):
            # If events is a string, try to parse it as JSON
            try:
                events_data = json.loads(events_data)
            except Exception:
                events_data = []

        return YahrzeitResponse(
            events=[
                YahrzeitEvent.from_api(cast("dict[str, Any]", item))
                for item in cast("list[Any]", events_data)
                if isinstance(item, dict)
            ],
            _data=data,
            _url=url,
            _params=params,
        )

    @property
    def raw(self) -> dict[str, Any]:
        return self._data or {}

    @property
    def query(self) -> str | None:
        if self._url and self._params:
            from urllib.parse import urlencode

            param_str = urlencode(self._params)
            return f"{self._url}?{param_str}"
        return None


@dataclass
class ConverterResponse:
    # Gregorian → Hebrew
    gy: int | None = None
    gm: int | None = None
    gd: int | None = None
    # Hebrew → Gregorian
    hy: int | None = None
    hm: str | None = None
    hd: int | None = None
    # Extra fields
    hebrew: str | None = None
    events: list[str] | None = None
    date: datetime | None = None  # Gregorian ISO string
    _data: dict[str, Any] | None = None  # Store raw data
    _url: str | None = None  # Store query URL
    _params: dict[str, Any] | None = None  # Store query params

    @staticmethod
    def from_api(
        data: dict[str, Any], url: str | None = None, params: dict[str, Any] | None = None
    ) -> "ConverterResponse":
        date_str = data.get("date")
        parsed_date = None
        if date_str:
            try:
                parsed_date = datetime.fromisoformat(str(date_str))
            except (ValueError, TypeError):
                parsed_date = None

        return ConverterResponse(
            gy=data.get("gy"),
            gm=data.get("gm"),
            gd=data.get("gd"),
            hy=data.get("hy"),
            hm=data.get("hm"),
            hd=data.get("hd"),
            hebrew=data.get("hebrew"),
            events=data.get("events"),
            date=parsed_date,
            _data=data,
            _url=url,
            _params=params,
        )

    @property
    def raw(self) -> dict[str, Any]:
        return self._data or {}

    @property
    def query(self) -> str | None:
        if self._url and self._params:
            from urllib.parse import urlencode

            param_str = urlencode(self._params)
            return f"{self._url}?{param_str}"
        return None
