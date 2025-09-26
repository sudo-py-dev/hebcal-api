from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from hebcal_api.tools.utils import remove_hebrew_nikud


class EventType(str, Enum):
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
    elevation: Optional[int] = None
    admin1: Optional[str] = None
    asciiname: Optional[str] = None
    geo: Optional[str] = None
    geonameid: Optional[int] = None


@dataclass
class OmerInfo:
    count_he: str
    count_en: str
    sefira_he: str
    sefira_translit: str
    sefira_en: str

    @property
    def count_he_non_nikud(self) -> str:
        return remove_hebrew_nikud(self.count_he)

    @property
    def sefira_he_non_nikud(self) -> str:
        return remove_hebrew_nikud(self.sefira_he)


@dataclass
class HolidayInfo:
    yomtov: Optional[bool] = None
    subcategory: Optional[str] = None
    memo: Optional[str] = None
    leyning: Optional[Dict[str, Any]] = None


@dataclass
class RangeInfo:
    start: datetime
    end: datetime


@dataclass
class HavdalahInfo:
    time: Optional[datetime] = None
    memo: Optional[str] = None


@dataclass
class CandleInfo:
    time: Optional[datetime] = None
    memo: Optional[str] = None


@dataclass
class ShabbatInfo:
    torah: Optional[str] = None
    haftarah: Optional[str] = None
    maftir: Optional[str] = None
    leyning: Optional[Dict[str, Any]] = None


@dataclass
class RoshChodeshInfo:
    link: Optional[str] = None
    torah: Optional[str] = None
    haftarah: Optional[str] = None
    maftir: Optional[str] = None
    portions: Optional[Dict[str, str]] = None  # For the '1', '2', etc.
    memo: Optional[str] = None

@dataclass
class ZmanimEvent:
    title: str                    # e.g. "תְּחִילַּת הַצוֹם"
    date: datetime                # datetime object with tzinfo
    type: EventType = EventType.ZMANIM
    hebrew: Optional[str] = None  # Hebrew string (e.g. "תחילת הצום")
    original_title: Optional[str] = None  # English/Original title
    memo: Optional[str] = None    # extra info (e.g. "צוֹם גְּדַלְיָה")
    subcat: Optional[str] = None  # sub-category ("fast", "sunrise", etc.)

    @property
    def title_non_nikud(self) -> str:
        return remove_hebrew_nikud(self.title)

    @property
    def memo_non_nikud(self) -> str:
        return remove_hebrew_nikud(self.memo)

@dataclass
class ParashatInfo:
    torah: Optional[str] = None
    haftarah: Optional[str] = None
    maftir: Optional[str] = None
    aliyot: Optional[Dict[str, str]] = None   # portions 1–7
    triennial: Optional[Dict[str, str]] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ParashatInfo":
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
    date: Optional[datetime] = None
    type: EventType = EventType.UNKNOWN
    hebrew: Optional[str] = None
    link: Optional[str] = None
    original_title: Optional[str] = None
    omer: Optional[OmerInfo] = None
    zmanim: Optional[ZmanimEvent] = None
    holiday: Optional[HolidayInfo] = None
    parashat: Optional[ParashatInfo] = None
    havdalah: Optional[HavdalahInfo] = None
    candle: Optional[CandleInfo] = None
    shabbat: Optional[ShabbatInfo] = None
    roshchodesh: Optional[RoshChodeshInfo] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Event":
        # Parse Omer info
        omer_info = None
        if "omer" in data:
            omer_info = OmerInfo(
                count_he=data["omer"]["count"].get("he", ""),
                count_en=data["omer"]["count"].get("en", ""),
                sefira_he=data["omer"]["sefira"].get("he", ""),
                sefira_translit=data["omer"]["sefira"].get("translit", ""),
                sefira_en=data["omer"]["sefira"].get("en", "")
            )

        # Parse Holiday info
        holiday_info = None
        if data.get("category") == "holiday":
            holiday_info = HolidayInfo(
                yomtov=data.get("yomtov", False),
                subcategory=data.get("subcat"),
                memo=data.get("memo"),
                leyning=data.get("leyning")
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
                leyning=leyning
            )

        zmanim_info = None
        if data.get("category") == "zmanim":
            zmanim_info = ZmanimEvent(
                title=data.get("title"),
                date=datetime.fromisoformat(data.get("date")) or None,
                type=EventType.ZMANIM,
                hebrew=data.get("hebrew"),
                original_title=data.get("title_orig"),
                memo=data.get("memo"),
                subcat=data.get("subcat")
            )

        # Parse Havdalah info
        havdalah_info = None
        if data.get("category") == "havdalah":
            havdalah_info = HavdalahInfo(
                time=datetime.fromisoformat(data.get("date")) or None,
                memo=data.get("memo")
            )

        # Parse Candle info
        candle_info = None
        if data.get("category") == "candles":
            candle_info = CandleInfo(
                time=datetime.fromisoformat(data.get("date")) or None,
                memo=data.get("memo")
            )

        # Parse Shabbat / Parashat info
        shabbat_info = None
        if data.get("category") in ("shabbat", "parashat") or "leyning" in data:
            leyning = data.get("leyning", {})
            shabbat_info = ShabbatInfo(
                torah=leyning.get("torah"),
                haftarah=leyning.get("haftarah"),
                maftir=leyning.get("maftir"),
                leyning=leyning
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
                memo=data.get("memo")
            )

        # Parse date safely
        event_date = None
        if "date" in data:
            try:
                event_date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
            except Exception:
                try:
                    event_date = datetime.strptime(data["date"], "%Y-%m-%d")
                except Exception:
                    event_date = None

        # Determine EventType safely
        category = data.get("category", "").lower()
        event_type = EventType(category) if category in EventType._value2member_map_ else EventType.UNKNOWN

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
            roshchodesh=roshchodesh_info
        )


class CalendarResponse:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def title(self) -> str:
        return self._data.get("title", "")

    @property
    def date(self) -> datetime:
        return datetime.fromisoformat(self._data.get("date", ""))

    @property
    def version(self) -> str:
        return self._data.get("version", "")

    @property
    def location(self) -> Location:
        return Location(
            title=self._data.get("location", {}).get("title", ""),
            city=self._data.get("location", {}).get("city", ""),
            tzid=self._data.get("location", {}).get("tzid", ""),
            latitude=self._data.get("location", {}).get("latitude", 0.0),
            longitude=self._data.get("location", {}).get("longitude", 0.0),
            cc=self._data.get("location", {}).get("cc", ""),
            country=self._data.get("location", {}).get("country", ""),
            elevation=self._data.get("location", {}).get("elevation", None),
            admin1=self._data.get("location", {}).get("admin1", None),
            asciiname=self._data.get("location", {}).get("asciiname", None),
            geo=self._data.get("location", {}).get("geo", None),
            geonameid=self._data.get("location", {}).get("geonameid", None)
        )

    @property
    def range(self) -> Optional[RangeInfo]:
        if self._data.get("range"):
            return RangeInfo(
                start=datetime.fromisoformat(self._data.get("range").get("start", "")),
                end=datetime.fromisoformat(self._data.get("range").get("end", ""))
            )
        return None

    @property
    def items(self) -> List[Event]:
        raw_items = self._data.get("items", [])
        return [Event.from_dict(item) for item in raw_items]

    @property
    def raw(self) -> Dict[str, Any]:
        return self._data


@dataclass
class ReadingPortion:
    k: str  # book
    b: str  # begin
    e: str  # end
    v: Optional[int] = None
    p: Optional[int] = None
    note: Optional[str] = None


@dataclass
class LeyningItem:
    date: datetime
    hdate: str
    type: str
    name_en: str
    name_he: str
    parshaNum: Optional[int] = None
    summary: Optional[str] = None
    summaryParts: Optional[List[Dict[str, str]]] = None
    fullkriyah: Optional[Dict[str, ReadingPortion]] = None
    haftara: Optional[str] = None
    haft: Optional[ReadingPortion] = None
    triennial: Optional[Dict[str, ReadingPortion]] = None
    triYear: Optional[int] = None
    triHaftara: Optional[str] = None
    triHaft: Optional[ReadingPortion] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LeyningItem":
        def parse_portion(d: Dict[str, Any]) -> Dict[str, ReadingPortion]:
            return {k: ReadingPortion(**v) for k, v in d.items()} if d else None

        return LeyningItem(
            date=datetime.fromisoformat(data["date"]),
            hdate=data.get("hdate", ""),
            type=data.get("type", ""),
            name_en=data.get("name", {}).get("en", ""),
            name_he=data.get("name", {}).get("he", ""),
            parshaNum=data.get("parshaNum"),
            summary=data.get("summary"),
            summaryParts=data.get("summaryParts"),
            fullkriyah=parse_portion(data.get("fullkriyah")),
            haftara=data.get("haftara"),
            haft=ReadingPortion(**data["haft"]) if data.get("haft") else None,
            triennial=parse_portion(data.get("triennial")),
            triYear=data.get("triYear"),
            triHaftara=data.get("triHaftara"),
            triHaft=ReadingPortion(**data["triHaft"]) if data.get("triHaft") else None
        )

    @property
    def name_he_non_nikud(self) -> str:
        return remove_hebrew_nikud(self.name_he)


@dataclass
class LeyningResponse:
    date: datetime
    location: str
    range_start: str
    range_end: str
    items: List[LeyningItem]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LeyningResponse":
        return LeyningResponse(
            date=datetime.fromisoformat(data["date"]),
            location=data.get("location", ""),
            range_start=data.get("range", {}).get("start", ""),
            range_end=data.get("range", {}).get("end", ""),
            items=[LeyningItem.from_dict(item) for item in data.get("items", [])]
        )


@dataclass
class ZmanimTimes:
    chatzotNight: Optional[str] = None
    alotHaShachar: Optional[str] = None
    misheyakir: Optional[str] = None
    misheyakirMachmir: Optional[str] = None
    dawn: Optional[str] = None
    sunrise: Optional[str] = None
    seaLevelSunrise: Optional[str] = None
    sofZmanShmaMGA19Point8: Optional[str] = None
    sofZmanShmaMGA16Point1: Optional[str] = None
    sofZmanShmaMGA: Optional[str] = None
    sofZmanShma: Optional[str] = None
    sofZmanTfillaMGA19Point8: Optional[str] = None
    sofZmanTfillaMGA16Point1: Optional[str] = None
    sofZmanTfillaMGA: Optional[str] = None
    sofZmanTfilla: Optional[str] = None
    chatzot: Optional[str] = None
    minchaGedola: Optional[str] = None
    minchaGedolaMGA: Optional[str] = None
    minchaKetana: Optional[str] = None
    minchaKetanaMGA: Optional[str] = None
    plagHaMincha: Optional[str] = None
    seaLevelSunset: Optional[str] = None
    sunset: Optional[str] = None
    beinHaShmashos: Optional[str] = None
    dusk: Optional[str] = None
    tzeit7083deg: Optional[str] = None
    tzeit85deg: Optional[str] = None
    tzeit42min: Optional[str] = None
    tzeit50min: Optional[str] = None
    tzeit72min: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZmanimTimes":
        return cls(**{k: data.get(k) for k in cls.__dataclass_fields__})


@dataclass
class ZmanimResponse:
    date: Any
    version: str
    location: Any
    times: ZmanimTimes

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ZmanimResponse":
        times_obj = ZmanimTimes.from_dict(data.get("times", {}))
        return cls(
            date=data["date"],
            version=data["version"],
            location=data["location"],
            times=times_obj
        )


@dataclass
class HebrewDateParts:
    yy: int
    mm: int
    dd: int
    month_name: str

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "HebrewDateParts":
        return HebrewDateParts(
            yy=data.get("yy"),
            mm=data.get("mm"),
            dd=data.get("dd"),
            month_name=data.get("month_name"),
        )


@dataclass
class YahrzeitEvent:
    title: str
    date: Optional[datetime] = None
    hebrew: Optional[str] = None
    category: str = ""
    anniversary: Optional[int] = None
    yahrzeitOf: Optional[str] = None
    heDateParts: Optional[HebrewDateParts] = None

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "YahrzeitEvent":
        date_str = data.get("date")
        parsed_date = None
        if date_str:
            try:
                parsed_date = datetime.fromisoformat(date_str)
            except (ValueError, TypeError):
                parsed_date = None

        return YahrzeitEvent(
            title=data.get("title"),
            date=parsed_date,
            hebrew=data.get("hebrew"),
            category=data.get("category"),
            anniversary=data.get("anniversary"),
            yahrzeitOf=data.get("yahrzeitOf"),
            heDateParts=HebrewDateParts.from_api(data["heDateParts"]) if "heDateParts" in data else None,
        )


@dataclass
class YahrzeitResponse:
    events: List[YahrzeitEvent]

    @staticmethod
    def from_api(data: List[Dict[str, Any]]) -> "YahrzeitResponse":
        return YahrzeitResponse(
            events=[YahrzeitEvent.from_api(item) for item in data]
        )


@dataclass
class ConverterResponse:
    # Gregorian → Hebrew
    gy: Optional[int] = None
    gm: Optional[int] = None
    gd: Optional[int] = None
    # Hebrew → Gregorian
    hy: Optional[int] = None
    hm: Optional[str] = None
    hd: Optional[int] = None
    # Extra fields
    hebrew: Optional[str] = None
    events: Optional[List[str]] = None
    date: Optional[datetime] = None  # Gregorian ISO string

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "ConverterResponse":
        date_str = data.get("date")
        parsed_date = None
        if date_str:
            try:
                parsed_date = datetime.fromisoformat(date_str)
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
        )
