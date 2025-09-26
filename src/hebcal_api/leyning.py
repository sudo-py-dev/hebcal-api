from typing import Optional, Dict, Any, Union
from datetime import datetime, date
from hebcal_api.tools.types import LeyningResponse
from .config import BASE_URL, DEFAULT_PARAMS
from .tools.utils import fetch_sync, fetch_async
from .tools.logger import logger

_ENDPOINT = "leyning"
_ALLOWED_PARAMS = {"date", "start", "end", "i", "triennial"}

class Leyning:
    def __init__(self):
        self.base_url = f"{BASE_URL}/{_ENDPOINT}"
        self.params: Dict[str, Any] = DEFAULT_PARAMS.copy()

    def _merge_params(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        merged = self.params.copy()
        if extra:
            for k, v in extra.items():
                if k not in _ALLOWED_PARAMS:
                    raise ValueError(f"Invalid extra parameter: '{k}'. Must be one of {sorted(_ALLOWED_PARAMS)}")
                merged[k] = v
        return merged

    def _format_datetime(self, dt: Union[str, datetime, date]) -> str:
        if isinstance(dt, datetime) or isinstance(dt, date):
            return dt.strftime("%Y-%m-%d")
        elif isinstance(dt, str):
            try:
                datetime.strptime(dt, "%Y-%m-%d")  # validation only
                return dt
            except ValueError:
                raise ValueError("Invalid datetime format '%Y-%m-%d' for parameter 'start' or 'end'")
        else:
            raise ValueError(f"dt not provaided or not in the right type {type(dt)}")

    def _validate_dates(
        self,
        date: Optional[Union[str, datetime, date]],
        start: Optional[Union[str, datetime, date]],
        end: Optional[Union[str, datetime, date]]
    ) -> Dict[str, str]:
        params: Dict[str, str] = {}
        if date:
            params["date"] = self._format_datetime(date)
        else:
            if not start or not end:
                raise ValueError("You must provide either a single 'date' or both 'start' and 'end'")
            start_dt = self._format_datetime(start)
            end_dt = self._format_datetime(end)
            if (datetime.strptime(end_dt, "%Y-%m-%d") - datetime.strptime(start_dt, "%Y-%m-%d")).days > 180:
                logger.warning("Date range > 180 days. Results will be truncated by the API.")
            params["start"] = start_dt
            params["end"] = end_dt
        return params

    def _prepare_params(
        self,
        date: Optional[Union[str, datetime, date]],
        start: Optional[Union[str, datetime, date]],
        end: Optional[Union[str, datetime, date]],
        diaspora: Optional[bool] = False,
        triennial: Optional[bool] = True
    ) -> Dict[str, Any]:
        params = self._validate_dates(date, start, end)
        params["i"] = "on" if diaspora else "off"
        params["triennial"] = "on" if triennial else "off"
        return self._merge_params(params)

    def get_leyning(
        self,
        date: Optional[Union[str, datetime, date]] = None,
        start: Optional[Union[str, datetime, date]] = None,
        end: Optional[Union[str, datetime, date]] = None,
        diaspora: Optional[bool] = False,
        triennial: Optional[bool] = True
    ) -> LeyningResponse:
        """
        Fetch Torah reading (Leyning) for a given date or date range.

        Parameters
        ----------
        date : Optional[str], default=None
            Gregorian date in ``YYYY-MM-DD`` format.
            Use this to request leyning for a single day.
            Cannot be combined with `start` or `end`.

        start : Optional[str], default=None
            Start date in ``YYYY-MM-DD`` format.
            Must be provided together with `end`.
            Defines the beginning of a date range (maximum 180 days).

        end : Optional[str], default=None
            End date in ``YYYY-MM-DD`` format.
            Must be provided together with `start`.
            Defines the end of a date range (maximum 180 days).

        diaspora : Optional[bool], default=False
            Whether to use Israel vs. Diaspora Torah readings and holidays.
            - ``False`` → Diaspora (default)
            - ``True`` → Israel

        triennial : Optional[bool], default=True
            Whether to include Triennial aliyot details.
            - ``True`` → include (default)
            - ``False`` → exclude to reduce response size

        Returns
        -------
        LeyningResponse
            Parsed leyning data, including aliyot and Torah portions.

        Raises
        ------
        ValueError
            If neither `date` nor both `start` and `end` are provided,
            or if the date range exceeds 180 days.
        """
        params = self._prepare_params(date, start, end, diaspora, triennial)
        logger.debug(f"Fetching Leyning from {self.base_url} with params {params}")
        data = fetch_sync(self.base_url, params=params)
        return LeyningResponse.from_dict(data, url=self.base_url, params=params)

    async def get_leyning_async(
        self,
        date: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        diaspora: Optional[bool] = False,
        triennial: Optional[bool] = True
    ) -> LeyningResponse:
        """
        Asynchronously fetch Torah reading (Leyning) for a given date or date range.

        Parameters
        ----------
        date : Optional[str], default=None
            Gregorian date in ``YYYY-MM-DD`` format.
            Use this to request leyning for a single day.
            Cannot be combined with `start` or `end`.

        start : Optional[str], default=None
            Start date in ``YYYY-MM-DD`` format.
            Must be provided together with `end`.
            Defines the beginning of a date range (maximum 180 days).

        end : Optional[str], default=None
            End date in ``YYYY-MM-DD`` format.
            Must be provided together with `start`.
            Defines the end of a date range (maximum 180 days).

        diaspora : Optional[bool], default=False
            Whether to use Israel vs. Diaspora Torah readings and holidays.
            - ``False`` → Diaspora (default)
            - ``True`` → Israel

        triennial : Optional[bool], default=True
            Whether to include Triennial aliyot details.
            - ``True`` → include (default)
            - ``False`` → exclude to reduce response size

        Returns
        -------
        LeyningResponse
            Parsed leyning data, including aliyot and Torah portions.

        Raises
        ------
        ValueError
            If neither `date` nor both `start` and `end` are provided,
            or if the date range exceeds 180 days.
        """
        params = self._prepare_params(date, start, end, diaspora, triennial)
        logger.debug(f"Fetching async Leyning from {self.base_url} with params {params}")
        data = await fetch_async(self.base_url, params=params)
        return LeyningResponse.from_dict(data, url=self.base_url, params=params)
