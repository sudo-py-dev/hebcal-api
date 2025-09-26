from typing import Optional, Dict, Any, Union
from datetime import datetime
from hebcal_api.tools.types import ZmanimResponse
from .config import BASE_URL, DEFAULT_PARAMS
from .tools.utils import fetch_sync, fetch_async
from .tools.logger import logger


_ENDPOINT = "zmanim"
_ALLOWED_PARAMS = {"date", "start", "end", "geonameid", "latitude", "longitude", "sec", "elevation"}

class Zmanim:

    def __init__(self):
        self.endpoint = f"{BASE_URL}/{_ENDPOINT}"
        self.params: Dict[str, Any] = DEFAULT_PARAMS.copy()

    def set_param(self, key: str, value: Any) -> "Zmanim":
        if key not in _ALLOWED_PARAMS:
            raise ValueError(f"Invalid parameter: '{key}'. Must be one of {sorted(_ALLOWED_PARAMS)}")
        if value is None:
            self.params.pop(key, None)
        else:
            self.params[key] = value
        return self

    def _merge_params(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        merged = self.params.copy()
        if extra:
            for k, v in extra.items():
                if k not in _ALLOWED_PARAMS:
                    raise ValueError(f"Invalid extra parameter: '{k}'. Must be one of {sorted(_ALLOWED_PARAMS)}")
                merged[k] = v
        return merged

    def _format_datetime(self, dt: Union[str, datetime]) -> str:
        """
        Ensure value is a valid YYYY-MM-DD string for the API.
        Accepts either datetime or string.
        """
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d")
        elif isinstance(dt, str):
            try:
                datetime.strptime(dt, "%Y-%m-%d")
                return dt
            except ValueError:
                raise ValueError("Invalid datetime format, must be 'YYYY-MM-DD'")
        else:
            raise TypeError("Date parameters must be either str or datetime")

    def _validate_dates(
        self,
        date: Optional[Union[str, datetime]],
        start: Optional[Union[str, datetime]],
        end: Optional[Union[str, datetime]]
    ) -> Dict[str, str]:
        params: Dict[str, str] = {}

        if date:
            params["date"] = self._format_datetime(date)
            return params
        else:
            if not start or not end:
                raise ValueError("You must provide either a single 'date' or both 'start' and 'end'")

        start_str = self._format_datetime(start)
        end_str = self._format_datetime(end)

        # validate range
        start_dt = datetime.strptime(start_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_str, "%Y-%m-%d")
        if (end_dt - start_dt).days > 180:
            logger.warning("Date range > 180 days. Results will be truncated by the API.")

        params["start"] = start_str
        params["end"] = end_str

        return params

    def _prepare_params(
        self,
        date: Optional[str],
        start: Optional[str],
        end: Optional[str],
        geonameid: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        sec: Optional[bool] = False,
        elevation: Optional[bool] = False
    ) -> Dict[str, Any]:
        params = self._validate_dates(date, start, end)
        if geonameid is not None:
            params["geonameid"] = geonameid
        if latitude is not None and longitude is not None:
            params["latitude"] = latitude
            params["longitude"] = longitude
        elif latitude is not None or longitude is not None:
            raise ValueError("Both latitude and longitude must be provided together")
        if sec:
            params["sec"] = 1
        if elevation:
            params["elevation"] = 1
        return self._merge_params(params)

    def get_zmanim(
        self,
        date: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        geonameid: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        sec: Optional[bool] = False,
        elevation: Optional[bool] = False
    ) -> ZmanimResponse:
        """
        Fetch Zmanim (halachic times) for a given location and date or date range.

        Parameters:
            date (str, optional): Single date in 'YYYY-MM-DD' format.
            start (str, optional): Start date for a range in 'YYYY-MM-DD' format.
            end (str, optional): End date for a range in 'YYYY-MM-DD' format.
            geonameid (int, optional): GeoNames.org numeric ID for the location.
            latitude (float, optional): Latitude of the location (requires longitude).
            longitude (float, optional): Longitude of the location (requires latitude).
            sec (bool, optional): If True, return times with second-level precision. Default is False.
            elevation (bool, optional): If True, use elevation-adjusted times for sunrise/sunset.

        Returns:
            ZmanimResponse: Typed dataclass containing the location info, date range, and zmanim times.

        Raises:
            ValueError: If date parameters are invalid or latitude/longitude are incomplete.
        """
        params = self._prepare_params(date, start, end, geonameid, latitude, longitude, sec, elevation)
        logger.debug(f"Fetching Zmanim from {self.endpoint} with params {params}")
        data = fetch_sync(self.endpoint, params=params)
        return ZmanimResponse.from_api(data)

    async def get_zmanim_async(
        self,
        date: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        geonameid: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        sec: Optional[bool] = False,
        elevation: Optional[bool] = False
    ) -> ZmanimResponse:
        """
        Asynchronously fetch Zmanim (halachic times) for a given location and date or date range.

        Parameters:
            date (str, optional): Single date in 'YYYY-MM-DD' format.
            start (str, optional): Start date for a range in 'YYYY-MM-DD' format.
            end (str, optional): End date for a range in 'YYYY-MM-DD' format.
            geonameid (int, optional): GeoNames.org numeric ID for the location.
            latitude (float, optional): Latitude of the location (requires longitude).
            longitude (float, optional): Longitude of the location (requires latitude).
            sec (bool, optional): If True, return times with second-level precision. Default is False.
            elevation (bool, optional): If True, use elevation-adjusted times for sunrise/sunset.

        Returns:
            ZmanimResponse: Typed dataclass containing the location info, date range, and zmanim times.

        Raises:
            ValueError: If date parameters are invalid or latitude/longitude are incomplete.
        """
        params = self._prepare_params(date, start, end, geonameid, latitude, longitude, sec, elevation)
        logger.debug(f"Fetching async Zmanim from {self.endpoint} with params {params}")
        data = await fetch_async(self.endpoint, params=params)
        return ZmanimResponse.from_api(data)
