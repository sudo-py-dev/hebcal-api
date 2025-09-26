from typing import Optional, Dict, Any
from hebcal_api.tools.types import CalendarResponse
from .config import BASE_URL, DEFAULT_PARAMS
from .tools.utils import fetch_sync, fetch_async
from .tools.logger import logger

_ENDPOINT = "shabbat"
_ALLOWED_PARAMS = {
        "b", "M", "m", "leyning", "gy", "gm", "gd", "hdp", "lg",
        "geonameid", "latitude", "longitude"
    }

class Shabat:
    def __init__(self):
        self.endpoint = f"{BASE_URL}/{_ENDPOINT}"
        self.params: Dict[str, Any] = DEFAULT_PARAMS.copy()

    def _merge_params(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        merged = self.params.copy()
        if extra:
            for k, v in extra.items():
                if k not in _ALLOWED_PARAMS:
                    raise ValueError(f"Invalid extra parameter: '{k}'. Must be one of {sorted(_ALLOWED_PARAMS)}")
                merged[k] = v
        return merged

    def _parse_params(self,
        # Location
        geonameid: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,

        # Candle/Havdalah
        candle_lighting: bool = True,
        candle_lighting_minutes_before_sunset: Optional[int] = 18,
        havdalah_minutes_after_sunset: Optional[int] = 42,
        havdalah_at_nightfall: bool = False,

        # Weekly Torah portion
        leyning: bool = False,

        # Config & language
        language: Optional[str] = None
    ) -> CalendarResponse:
        params: Dict[str, Any] = {}

        # ----------------------------
        # Location validation
        # ----------------------------
        location_provided = 0
        if geonameid is not None:
            if not isinstance(geonameid, int) or geonameid <= 0:
                raise ValueError("geonameid must be a positive integer")
            params["geonameid"] = geonameid
            location_provided += 1
        if latitude is not None or longitude is not None:
            if latitude is None or longitude is None:
                raise ValueError("Both latitude and longitude must be provided together")
            params["latitude"] = latitude
            params["longitude"] = longitude
            location_provided += 1
        if location_provided == 0:
            raise ValueError("You must provide at least one location: geonameid or latitude+longitude")
        if location_provided > 1:
            raise ValueError("Provide only one location method: geonameid OR latitude+longitude")

        # ----------------------------
        # Candle/Havdalah
        # ----------------------------
        if candle_lighting and candle_lighting_minutes_before_sunset is not None:
            if candle_lighting_minutes_before_sunset < 0:
                raise ValueError("candle_lighting_minutes_before_sunset must be >= 0")
            params["b"] = candle_lighting_minutes_before_sunset
        if havdalah_minutes_after_sunset is not None:
            if havdalah_minutes_after_sunset < 0:
                raise ValueError("havdalah_minutes_after_sunset must be >= 0")
            params["m"] = havdalah_minutes_after_sunset
        if havdalah_at_nightfall:
            params["M"] = "on"

        # ----------------------------
        # Weekly Torah portion
        # ----------------------------
        if leyning:
            params["leyning"] = "on"

        # ----------------------------
        # language
        # ----------------------------
        if language:
            params["lg"] = language

        # ----------------------------
        # Merge with default parameters
        # ----------------------------
        params = self._merge_params(params)
        return params

    # ----------------------------
    # Full get_shabbat function
    # ----------------------------
    def get_shabbat(
        self,
        geonameid: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        candle_lighting: bool = True,
        candle_lighting_minutes_before_sunset: Optional[int] = 18,
        havdalah_minutes_after_sunset: Optional[int] = 42,
        havdalah_at_nightfall: bool = False,
        leyning: bool = False,
        language: Optional[str] = None
    ) -> CalendarResponse:
        """
        Fetch Shabbat times for a specific location.

        Parameters
        ----------
        geonameid : Optional[int], default=None
            Geonames.org ID for the location. Overrides latitude and longitude if provided.
        latitude : Optional[float], default=None
            Latitude of the location (used if geonameid is not provided).
        longitude : Optional[float], default=None
            Longitude of the location (used if geonameid is not provided).
        candle_lighting : bool, default=True
            Include candle lighting times.
        candle_lighting_minutes_before_sunset : Optional[int], default=18
            Minutes before sunset for candle lighting.
        havdalah_minutes_after_sunset : Optional[int], default=42
            Minutes after sunset for Havdalah.
        havdalah_at_nightfall : bool, default=False
            Calculate Havdalah at nightfall instead of fixed minutes.
        leyning : bool, default=False
            Include the weekly Torah portion (Parashat) readings.
        language : Optional[str], default=None
            Language code for returned text (e.g., 'en', 'he').

        Returns
        -------
        CalendarResponse
            A response object containing Shabbat times, candle lighting, Havdalah,
            and optional Torah portion information.

        Notes
        -----
        This method calls the synchronous API and returns a `CalendarResponse` object.
        """
        params = self._parse_params(
            geonameid=geonameid,
            latitude=latitude,
            longitude=longitude,
            candle_lighting=candle_lighting,
            candle_lighting_minutes_before_sunset=candle_lighting_minutes_before_sunset,
            havdalah_minutes_after_sunset=havdalah_minutes_after_sunset,
            havdalah_at_nightfall=havdalah_at_nightfall,
            leyning=leyning,
            language=language
        )
        logger.debug(f"Fetching Shabbat times from {self.endpoint} with params {params}")
        return CalendarResponse(fetch_sync(self.endpoint, params=params), url=self.endpoint, params=params)


    async def get_shabbat_async(
        self,
        geonameid: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        candle_lighting: bool = True,
        candle_lighting_minutes_before_sunset: Optional[int] = 18,
        havdalah_minutes_after_sunset: Optional[int] = 42,
        havdalah_at_nightfall: bool = False,
        leyning: bool = False,
        language: Optional[str] = None
    ) -> CalendarResponse:
        """
        Asynchronously fetch Shabbat times for a specific location.

        Parameters
        ----------
        geonameid : Optional[int], default=None
            Geonames.org ID for the location. Overrides latitude and longitude if provided.
        latitude : Optional[float], default=None
            Latitude of the location (used if geonameid is not provided).
        longitude : Optional[float], default=None
            Longitude of the location (used if geonameid is not provided).
        candle_lighting : bool, default=True
            Include candle lighting times.
        candle_lighting_minutes_before_sunset : Optional[int], default=18
            Minutes before sunset for candle lighting.
        havdalah_minutes_after_sunset : Optional[int], default=42
            Minutes after sunset for Havdalah.
        havdalah_at_nightfall : bool, default=False
            Calculate Havdalah at nightfall instead of fixed minutes.
        leyning : bool, default=False
            Include the weekly Torah portion (Parashat) readings.
        language : Optional[str], default=None
            Language code for returned text (e.g., 'en', 'he').

        Returns
        -------
        CalendarResponse
            A response object containing Shabbat times, candle lighting, Havdalah,
            and optional Torah portion information.

        Notes
        -----
        This method calls the asynchronous API and returns a `CalendarResponse` object.
        """
        params = self._parse_params(
            geonameid=geonameid,
            latitude=latitude,
            longitude=longitude,
            candle_lighting=candle_lighting,
            candle_lighting_minutes_before_sunset=candle_lighting_minutes_before_sunset,
            havdalah_minutes_after_sunset=havdalah_minutes_after_sunset,
            havdalah_at_nightfall=havdalah_at_nightfall,
            leyning=leyning,
            language=language
        )
        logger.debug(f"Fetching async Shabbat times from {self.endpoint} with params {params}")
        return CalendarResponse(await fetch_async(self.endpoint, params=params), url=self.endpoint, params=params)
