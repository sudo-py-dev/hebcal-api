from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from .config import BASE_URL, DEFAULT_PARAMS
from .tools.utils import fetch_sync, fetch_async
from .tools.logger import logger
from .tools.types import ConverterResponse


_ENDPOINT = "converter"
_ALLOWED_PARAMS = {
    "cfg", "date", "start", "end", "g2h", "h2g", "strict", "gs",
    "gy", "gm", "gd", "hy", "hm", "hd", "ndays", "lg", "callback"
}


class Converter:
    """
    Python wrapper for the Hebcal Hebrew Date Converter API.
    Supports conversions between Gregorian <-> Hebrew (single dates and ranges).
    """

    def __init__(self):
        self.endpoint = f"{BASE_URL}/{_ENDPOINT}"
        self.params: Dict[str, Any] = DEFAULT_PARAMS.copy()
        self.params["cfg"] = "json"

    def set_param(self, key: str, value: Any) -> "Converter":
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
                    raise ValueError(f"Invalid extra parameter: '{k}'")
                merged[k] = v
        return merged

    def _format_date(self, dt: Union[str, datetime]) -> str:
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d")
        elif isinstance(dt, str):
            datetime.strptime(dt, "%Y-%m-%d")  # validation
            return dt
        else:
            raise TypeError("Date must be str or datetime")

    # ----------------------
    # Gregorian → Hebrew
    # ----------------------

    def g2h_single(
        self,
        date: Union[str, datetime],
        after_sunset: bool = False,
        strict: bool = True
    ) -> ConverterResponse:
        """
        Convert a single Gregorian date into its Hebrew date equivalent.

        Args:
            date (Union[str, datetime]): Gregorian date, either as a string (YYYY-MM-DD) or `datetime`.
            after_sunset (bool, optional): If True, treat the given Gregorian date as *after sunset*,
                which means the Hebrew date will roll over to the next day. Defaults to False.
            strict (bool, optional): If True, enforces strict validation of input. Defaults to True.

        Returns:
            ConverterResponse: Typed response containing the Hebrew date information.
        """
        params = self._merge_params({
            "date": self._format_date(date),
            "g2h": 1,
            "strict": 1 if strict else 0,
        })
        if after_sunset:
            params["gs"] = "on"
        logger.debug(f"Fetching g2h (single) from {self.endpoint} with params {params}")
        data = fetch_sync(self.endpoint, params=params)
        return ConverterResponse.from_api(data, url=self.endpoint, params=params)

    async def g2h_single_async(
        self,
        date: Union[str, datetime],
        after_sunset: bool = False,
        strict: bool = True
    ) -> ConverterResponse:
        """
        Async version of `g2h_single`.

        Converts a single Gregorian date into its Hebrew date equivalent.

        Args:
            date (Union[str, datetime]): Gregorian date as string or `datetime`.
            after_sunset (bool, optional): Apply sunset adjustment. Defaults to False.
            strict (bool, optional): Enforce input validation. Defaults to True.

        Returns:
            ConverterResponse: Typed Hebrew date response.
        """
        params = self._merge_params({
            "date": self._format_date(date),
            "g2h": 1,
            "strict": 1 if strict else 0,
        })
        if after_sunset:
            params["gs"] = "on"
        logger.debug(f"Fetching async g2h (single) from {self.endpoint} with params {params}")
        data = await fetch_async(self.endpoint, params=params)
        return ConverterResponse.from_api(data, url=self.endpoint, params=params)

    def g2h_range(
        self,
        start: Union[str, datetime],
        end: Union[str, datetime]
    ) -> List[ConverterResponse]:
        """
        Convert a range of Gregorian dates into Hebrew dates.

        Args:
            start (Union[str, datetime]): Start date of the range.
            end (Union[str, datetime]): End date of the range.

        Returns:
            List[ConverterResponse]: List of Hebrew date conversions for each day in the range.
        """
        params = self._merge_params({
            "start": self._format_date(start),
            "end": self._format_date(end),
            "g2h": 1,
        })
        logger.debug(f"Fetching g2h (range) from {self.endpoint} with params {params}")
        data = fetch_sync(self.endpoint, params=params)
        return [ConverterResponse.from_api(item, url=self.endpoint, params=params) for item in data]

    # ----------------------
    # Hebrew → Gregorian
    # ----------------------

    def h2g_single(
        self,
        year: int,
        month: str,
        day: int,
        strict: bool = True
    ) -> ConverterResponse:
        """
        Convert a single Hebrew date into its Gregorian date equivalent.

        Args:
            year (int): Hebrew year (e.g., 5785).
            month (str): Hebrew month (e.g., 'Nisan').
            day (int): Hebrew day of the month.
            strict (bool, optional): Enforce validation rules. Defaults to True.

        Returns:
            ConverterResponse: Typed Gregorian date response.
        """
        params = self._merge_params({
            "hy": year,
            "hm": month,
            "hd": day,
            "h2g": 1,
            "strict": 1 if strict else 0,
        })
        logger.debug(f"Fetching h2g (single) from {self.endpoint} with params {params}")
        data = fetch_sync(self.endpoint, params=params)
        return ConverterResponse.from_api(data, url=self.endpoint, params=params)

    async def h2g_single_async(
        self,
        year: int,
        month: str,
        day: int,
        strict: bool = True
    ) -> ConverterResponse:
        """
        Async version of `h2g_single`.

        Convert a Hebrew date into its Gregorian equivalent.

        Args:
            year (int): Hebrew year.
            month (str): Hebrew month name.
            day (int): Day of the month.
            strict (bool, optional): Input validation toggle. Defaults to True.

        Returns:
            ConverterResponse: Gregorian date response.
        """
        params = self._merge_params({
            "hy": year,
            "hm": month,
            "hd": day,
            "h2g": 1,
            "strict": 1 if strict else 0,
        })
        logger.debug(f"Fetching async h2g (single) from {self.endpoint} with params {params}")
        data = await fetch_async(self.endpoint, params=params)
        return ConverterResponse.from_api(data, url=self.endpoint, params=params)

    def h2g_range(
        self,
        year: int,
        month: str,
        day: int,
        ndays: int = 30,
        strict: bool = True
    ) -> List[ConverterResponse]:
        """
        Convert a sequence of Hebrew dates into Gregorian equivalents.

        Args:
            year (int): Hebrew year.
            month (str): Hebrew month name.
            day (int): Starting Hebrew day.
            ndays (int, optional): Number of days to convert (2–180). Defaults to 30.
            strict (bool, optional): Enforce validation. Defaults to True.

        Raises:
            ValueError: If `ndays` is outside the allowed range (2–180).

        Returns:
            List[ConverterResponse]: List of Gregorian date responses.
        """
        if ndays < 2 or ndays > 180:
            raise ValueError("ndays must be between 2 and 180")
        params = self._merge_params({
            "hy": year,
            "hm": month,
            "hd": day,
            "h2g": 1,
            "ndays": ndays,
            "strict": 1 if strict else 0,
        })
        logger.debug(f"Fetching h2g (range) from {self.endpoint} with params {params}")
        data = fetch_sync(self.endpoint, params=params)
        return [ConverterResponse.from_api(item, url=self.endpoint, params=params) for item in data]
