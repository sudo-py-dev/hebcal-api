from typing import Optional, Dict, Any, Union
from datetime import date, datetime
from hebcal_api.tools.types import CalendarResponse
from .config import BASE_URL, DEFAULT_PARAMS
from .tools.utils import fetch_sync, fetch_async
from .tools.logger import logger


_ENDPOINT = "hebcal"
_ALLOWED_PARAMS = {
        "v", "cfg", "year", "yt", "month", "ny", "start", "end",
        "geonameid", "zip", "latitude", "longitude", "tzid", "city",
        "maj", "yto", "min", "nx", "mf", "ss", "mod", "s", "leyning",
        "D", "d", "o", "ykk", "molad", "yzkr", "mvch",
        "i", "c", "b", "m", "M",
        "F", "dw", "yyomi", "yys", "myomi", "nyomi",
        "dty", "dps", "dr1", "dr3", "dsm", "dksa", "ahsy",
        "dcc", "dshl", "dpa", "hdp", "lg"
    }


class Calendar:
    """
    Python wrapper for the Hebcal Jewish Calendar REST API.

    Allows fetching events, holidays, Shabbat times, Omer days, and daily learning schedules.
    All parameters are validated according to the Hebcal API documentation.
    """
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

    def _parse_params(        self,
        # Date parameters
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        year: Optional[Union[str, int]] = None,
        year_type: Optional[str] = None,
        month: Optional[Union[int, str]] = None,
        number_of_years: Optional[int] = None,

        # Location
        geonameid: Optional[int] = None,
        zip_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone_id: Optional[str] = None,
        city_name: Optional[str] = None,

        # Israel/Diaspora
        israel_holidays_and_torah_readings: Optional[bool] = None,

        # Holidays and Events
        major_holidays: bool = False,
        yom_tov_only: bool = False,
        minor_holidays: bool = False,
        rosh_chodesh: bool = False,
        minor_fasts: bool = False,
        special_shabbatot: bool = False,
        modern_holidays: bool = False,
        weekly_torah_portion: bool = False,
        include_leyning: bool = False,
        hebrew_date_for_events: bool = False,
        hebrew_date_for_range: bool = False,
        omer_days: bool = False,
        yom_kippur_katan: bool = False,
        molad_dates: bool = False,
        yizkor_dates: bool = False,
        shabbat_mevarchim: bool = False,

        # Candle/Havdalah
        candle_lighting_times: bool = False,
        candle_lighting_minutes_before_sunset: Optional[int] = None,
        havdalah_minutes_after_sunset: Optional[int] = None,
        havdalah_at_nightfall: bool = False,

        # Daily Learning
        daf_yomi: bool = False,
        daf_a_week: bool = False,
        yerushalmi_yomi_vilna: bool = False,
        yerushalmi_yomi_schottenstein: bool = False,
        mishna_yomi: bool = False,
        nach_yomi: bool = False,
        tanakh_yomi: bool = False,
        daily_tehillim: bool = False,
        daily_rambam_1_chapter: bool = False,
        daily_rambam_3_chapters: bool = False,
        sefer_ha_mitzvot: bool = False,
        kitzur_shulchan_arukh_yomi: bool = False,
        arukh_ha_shulchan_yomi: bool = False,
        sefer_chofetz_chaim: bool = False,
        shemirat_ha_lashon: bool = False,
        pirkei_avot_shabbatot: bool = False,

        # Misc
        holiday_description_only: bool = False,
        language: Optional[str] = None) -> CalendarResponse:
                # Validate dates and location
        params = self._validate_date_params(start, end, year, year_type, month, number_of_years)
        if params is None:
            raise ValueError("m\n\n\n")
        params.update(self._validate_location_params(geonameid, zip_code, latitude, longitude, timezone_id, city_name))

        # Israel flag
        if israel_holidays_and_torah_readings is not None:
            params["i"] = "on" if israel_holidays_and_torah_readings else "off"

        # Candle/Havdalah
        if candle_lighting_minutes_before_sunset is not None:
            if candle_lighting_minutes_before_sunset < 0:
                raise ValueError("candle_lighting_minutes_before_sunset must be >= 0")
            params["b"] = candle_lighting_minutes_before_sunset
        if havdalah_minutes_after_sunset is not None:
            if havdalah_minutes_after_sunset < 0:
                raise ValueError("havdalah_minutes_after_sunset must be >= 0")
            params["m"] = havdalah_minutes_after_sunset
        if havdalah_at_nightfall:
            params["M"] = "on"

        # Map event flags
        event_flags = {
            "maj": major_holidays, "yto": yom_tov_only, "min": minor_holidays,
            "nx": rosh_chodesh, "mf": minor_fasts, "ss": special_shabbatot,
            "mod": modern_holidays, "s": weekly_torah_portion, "leyning": include_leyning,
            "D": hebrew_date_for_events, "d": hebrew_date_for_range, "o": omer_days,
            "ykk": yom_kippur_katan, "molad": molad_dates, "yzkr": yizkor_dates,
            "mvch": shabbat_mevarchim, "c": candle_lighting_times,
            "F": daf_yomi, "dw": daf_a_week, "yyomi": yerushalmi_yomi_vilna,
            "yys": yerushalmi_yomi_schottenstein, "myomi": mishna_yomi, "nyomi": nach_yomi,
            "dty": tanakh_yomi, "dps": daily_tehillim, "dr1": daily_rambam_1_chapter,
            "dr3": daily_rambam_3_chapters, "dsm": sefer_ha_mitzvot, "dksa": kitzur_shulchan_arukh_yomi,
            "ahsy": arukh_ha_shulchan_yomi, "dcc": sefer_chofetz_chaim, "dshl": shemirat_ha_lashon,
            "dpa": pirkei_avot_shabbatot, "hdp": holiday_description_only, "lg": language
        }
        for k, v in event_flags.items():
            if isinstance(v, bool) and v:
                params[k] = "on"
            elif v not in (None, False):
                params[k] = v
        return params

    def _get_calendar_sync(self, extra_params: Optional[Dict[str, Any]] = None) -> CalendarResponse:
        """
        Fetch the Jewish calendar synchronously from Hebcal API.

        This method allows you to pass any parameter supported by the Hebcal API.
        For event-specific queries, consider using the `get_events` method.

        API Documentation:
            https://www.hebcal.com/home/195/jewish-calendar-rest-api

        Args:
            extra_params (Optional[Dict[str, Any]]): Additional query parameters for the API.

        Returns:
            CalendarResponse: Parsed response containing calendar items.

        Raises:
            FetchError: If there is an issue fetching data from the API.
            ValueError: If the response data is invalid.
        """
        # Merge default and extra parameters
        params = self._merge_params(extra_params or {})

        logger.debug(f"Fetching calendar synchronously from {self.endpoint} with params: {params}")
        response_data = fetch_sync(self.endpoint, params=params)

        if not isinstance(response_data, dict):
            logger.error(f"Unexpected response format: {type(response_data)}")
            raise ValueError("Invalid response data format from Hebcal API")

        return CalendarResponse(response_data)

    async def _get_calendar_async(self, extra_params: Optional[Dict[str, Any]] = None) -> CalendarResponse:
        """
        Fetch the Jewish calendar asynchronously from Hebcal API.

        This method allows you to pass any parameter supported by the Hebcal API.
        For event-specific queries, consider using the `get_events` method.

        API Documentation:
            https://www.hebcal.com/home/195/jewish-calendar-rest-api

        Args:
            extra_params (Optional[Dict[str, Any]]): Extra query parameters for the API. Defaults to None.

        Returns:
            CalendarResponse: The parsed calendar response.

        Raises:
            FetchError: If fetching data from the API fails.
            ValueError: If the response data is not a dictionary.
        """
        params = self._merge_params(extra_params or {})
        logger.debug(f"Fetching async from {self.endpoint} with params: {params}")

        response_data = await fetch_async(self.endpoint, params=params)

        if not isinstance(response_data, dict):
            logger.error(f"Unexpected response format: {type(response_data)}")
            raise ValueError("Invalid response data format from Hebcal API")

        return CalendarResponse(response_data)

    def _format_datetime(self, dt: Union[str, datetime, date]) -> str:
        if isinstance(dt, datetime) or isinstance(dt, date):
            return dt.strftime("%Y-%m-%d")
        elif isinstance(dt, str):
            try:
                return datetime.strptime(dt, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid datetime format '%Y-%m-%d' for parameter 'start' or 'end'")
        else:
            raise ValueError(f"dt not provaided or not in the right type {type(dt)}")

    def _validate_date_params(
        self,
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        year: Optional[Union[str, int]] = None,
        yt: Optional[str] = None,
        month: Optional[Union[int, str]] = None,
        ny: Optional[int] = None,
    ) -> Dict[str, Any]:
        if year is not None and (start or end):
            raise ValueError("Cannot specify both 'year' and 'start/end'. Choose one method.")
        if year is not None:
            params = {"year": year}
            if yt:
                if yt not in ("G", "H"):
                    raise ValueError("yt must be 'G' or 'H'")
                params["yt"] = yt
            if month:
                if month != "x" and not (1 <= int(month) <= 12):
                    raise ValueError("month must be 'x' or 1-12")
                params["month"] = month
            if ny is not None:
                if ny < 1:
                    raise ValueError("ny must be >= 1")
                params["ny"] = ny
            return params
        elif start and end:
            return {"start": self._format_datetime(start), "end": self._format_datetime(end)}
        else:
            raise ValueError("Provide either 'start' and 'end' (str, date, datetime) or a 'year'.")


    def _validate_location_params(
        self,
        geonameid: Optional[int] = None,
        zip_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        tzid: Optional[str] = None,
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        provided = []
        if geonameid is not None:
            if not isinstance(geonameid, int) or geonameid <= 0:
                raise ValueError("geonameid must be a positive integer")
            provided.append("geonameid")
        if zip_code is not None:
            if not (isinstance(zip_code, str) and zip_code.isdigit() and len(zip_code) == 5):
                raise ValueError("zip must be a 5-digit string")
            provided.append("zip")
        if any([latitude, longitude, tzid]):
            if latitude is None or longitude is None or tzid is None:
                raise ValueError("latitude, longitude, and tzid must all be provided together")
            provided.append("latlon")
        if city is not None:
            provided.append("city")
        if len(provided) == 0:
            raise ValueError("You must provide one location parameter")
        if len(provided) > 1:
            raise ValueError(f"Only one location parameter is allowed. Provided: {provided}")
        if geonameid is not None:
            return {"geonameid": geonameid}
        if zip_code is not None:
            return {"zip": zip_code}
        if latitude is not None:
            return {"latitude": latitude, "longitude": longitude, "tzid": tzid}
        if city is not None:
            return {"city": city}

    # ----------------------------
    # Main event function
    # ----------------------------
    def get_events(
        self,
        # Date parameters
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        year: Optional[Union[str, int]] = None,
        year_type: Optional[str] = None,
        month: Optional[Union[int, str]] = None,
        number_of_years: Optional[int] = None,

        # Location
        geonameid: Optional[int] = None,
        zip_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone_id: Optional[str] = None,
        city_name: Optional[str] = None,

        # Israel/Diaspora
        israel_holidays_and_torah_readings: Optional[bool] = None,

        # Holidays and Events
        major_holidays: bool = False,
        yom_tov_only: bool = False,
        minor_holidays: bool = False,
        rosh_chodesh: bool = False,
        minor_fasts: bool = False,
        special_shabbatot: bool = False,
        modern_holidays: bool = False,
        weekly_torah_portion: bool = False,
        include_leyning: bool = False,
        hebrew_date_for_events: bool = False,
        hebrew_date_for_range: bool = False,
        omer_days: bool = False,
        yom_kippur_katan: bool = False,
        molad_dates: bool = False,
        yizkor_dates: bool = False,
        shabbat_mevarchim: bool = False,

        # Candle/Havdalah
        candle_lighting_times: bool = False,
        candle_lighting_minutes_before_sunset: Optional[int] = None,
        havdalah_minutes_after_sunset: Optional[int] = None,
        havdalah_at_nightfall: bool = False,

        # Daily Learning
        daf_yomi: bool = False,
        daf_a_week: bool = False,
        yerushalmi_yomi_vilna: bool = False,
        yerushalmi_yomi_schottenstein: bool = False,
        mishna_yomi: bool = False,
        nach_yomi: bool = False,
        tanakh_yomi: bool = False,
        daily_tehillim: bool = False,
        daily_rambam_1_chapter: bool = False,
        daily_rambam_3_chapters: bool = False,
        sefer_ha_mitzvot: bool = False,
        kitzur_shulchan_arukh_yomi: bool = False,
        arukh_ha_shulchan_yomi: bool = False,
        sefer_chofetz_chaim: bool = False,
        shemirat_ha_lashon: bool = False,
        pirkei_avot_shabbatot: bool = False,

        # Misc
        holiday_description_only: bool = False,
        language: Optional[str] = None
    ) -> CalendarResponse:
        params = self._parse_params(
            start, end, year, year_type, month, number_of_years,
            geonameid, zip_code, latitude, longitude, timezone_id, city_name,
            israel_holidays_and_torah_readings,
            major_holidays, yom_tov_only, minor_holidays, rosh_chodesh, minor_fasts, special_shabbatot,
            modern_holidays, weekly_torah_portion, include_leyning, hebrew_date_for_events, hebrew_date_for_range,
            omer_days, yom_kippur_katan, molad_dates, yizkor_dates, shabbat_mevarchim,
            candle_lighting_times, candle_lighting_minutes_before_sunset, havdalah_minutes_after_sunset, havdalah_at_nightfall,
            daf_yomi, daf_a_week, yerushalmi_yomi_vilna, yerushalmi_yomi_schottenstein, mishna_yomi, nach_yomi, tanakh_yomi,
            daily_tehillim, daily_rambam_1_chapter, daily_rambam_3_chapters, sefer_ha_mitzvot, kitzur_shulchan_arukh_yomi,
            arukh_ha_shulchan_yomi, sefer_chofetz_chaim, shemirat_ha_lashon, pirkei_avot_shabbatot,
            holiday_description_only, language
        )
        return self._get_calendar_sync(params)


    async def get_events_async(
        self,
        # Date parameters
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        year: Optional[Union[str, int]] = None,
        year_type: Optional[str] = None,  # 'G' = Gregorian, 'H' = Hebrew
        month: Optional[Union[int, str]] = None,
        number_of_years: Optional[int] = None,

        # Location
        geonameid: Optional[int] = None,
        zip_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone_id: Optional[str] = None,
        city_name: Optional[str] = None,

        # Israel/Diaspora
        israel_holidays_and_torah_readings: Optional[bool] = None,

        # Holidays and Events
        major_holidays: bool = False,
        yom_tov_only: bool = False,
        minor_holidays: bool = False,
        rosh_chodesh: bool = False,
        minor_fasts: bool = False,
        special_shabbatot: bool = False,
        modern_holidays: bool = False,
        weekly_torah_portion: bool = False,
        include_leyning: bool = False,
        hebrew_date_for_events: bool = False,
        hebrew_date_for_range: bool = False,
        omer_days: bool = False,
        yom_kippur_katan: bool = False,
        molad_dates: bool = False,
        yizkor_dates: bool = False,
        shabbat_mevarchim: bool = False,

        # Candle/Havdalah
        candle_lighting_times: bool = False,
        candle_lighting_minutes_before_sunset: Optional[int] = None,
        havdalah_minutes_after_sunset: Optional[int] = None,
        havdalah_at_nightfall: bool = False,

        # Daily Learning
        daf_yomi: bool = False,
        daf_a_week: bool = False,
        yerushalmi_yomi_vilna: bool = False,
        yerushalmi_yomi_schottenstein: bool = False,
        mishna_yomi: bool = False,
        nach_yomi: bool = False,
        tanakh_yomi: bool = False,
        daily_tehillim: bool = False,
        daily_rambam_1_chapter: bool = False,
        daily_rambam_3_chapters: bool = False,
        sefer_ha_mitzvot: bool = False,
        kitzur_shulchan_arukh_yomi: bool = False,
        arukh_ha_shulchan_yomi: bool = False,
        sefer_chofetz_chaim: bool = False,
        shemirat_ha_lashon: bool = False,
        pirkei_avot_shabbatot: bool = False,

        # Misc
        holiday_description_only: bool = False,
        language: Optional[str] = None
    ) -> CalendarResponse:
        params = self._parse_params(
            start, end, year, year_type, month, number_of_years,
            geonameid, zip_code, latitude, longitude, timezone_id, city_name,
            israel_holidays_and_torah_readings,
            major_holidays, yom_tov_only, minor_holidays, rosh_chodesh, minor_fasts, special_shabbatot,
            modern_holidays, weekly_torah_portion, include_leyning, hebrew_date_for_events, hebrew_date_for_range,
            omer_days, yom_kippur_katan, molad_dates, yizkor_dates, shabbat_mevarchim,
            candle_lighting_times, candle_lighting_minutes_before_sunset, havdalah_minutes_after_sunset, havdalah_at_nightfall,
            daf_yomi, daf_a_week, yerushalmi_yomi_vilna, yerushalmi_yomi_schottenstein, mishna_yomi, nach_yomi, tanakh_yomi,
            daily_tehillim, daily_rambam_1_chapter, daily_rambam_3_chapters, sefer_ha_mitzvot, kitzur_shulchan_arukh_yomi,
            arukh_ha_shulchan_yomi, sefer_chofetz_chaim, shemirat_ha_lashon, pirkei_avot_shabbatot,
            holiday_description_only, language
        )
        return await self._get_calendar_async(params)