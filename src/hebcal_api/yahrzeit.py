from typing import Optional, Dict, Any
from .config import BASE_URL, DEFAULT_PARAMS
from .tools.utils import fetch_sync, fetch_async
from .tools.logger import logger
from .tools.types import YahrzeitResponse

_ENDPOINT = "yahrzeit"
_ALLOWED_PARAMS = {
    "cfg", "v", "years", "hebdate", "yizkor", "i",
    "start", "end", "hdp",
    # dynamic inputs y1,m1,d1,s1,t1,n1 ... yN,mN,dN,sN,tN,nN
}


class Yahrzeit:
    """
    Python wrapper for Hebcal Yahrzeit + Anniversary API.

    Supports Yahrzeit, Hebrew Birthday, and Anniversary calculations.
    """

    def __init__(self):
        self.endpoint = f"{BASE_URL}/{_ENDPOINT}"
        self.params: Dict[str, Any] = DEFAULT_PARAMS.copy()
        # Required defaults
        self.params["cfg"] = "json"
        self.params["v"] = "yahrzeit"

    def set_param(self, key: str, value: Any) -> "Yahrzeit":
        if key not in _ALLOWED_PARAMS and not key[0] in {"y", "m", "d", "s", "t", "n"}:
            raise ValueError(f"Invalid parameter: '{key}'. Must be one of {sorted(_ALLOWED_PARAMS)}")
        if value is None:
            self.params.pop(key, None)
        else:
            self.params[key] = value
        return self

    def add_event(
        self,
        index: int,
        year: int,
        month: int,
        day: int,
        after_sunset: bool = False,
        event_type: str = "Yahrzeit",
        name: Optional[str] = None,
    ) -> "Yahrzeit":
        """
        Add a Yahrzeit/Birthday/Anniversary event to the request.

        Parameters:
            index (int): Event number (1-based).
            year (int): Gregorian year of event.
            month (int): Gregorian month (1–12).
            day (int): Gregorian day (1–31).
            after_sunset (bool): Whether the event occurred after sunset.
            event_type (str): One of 'Yahrzeit', 'Birthday', or 'Anniversary'.
            name (str, optional): Name of the person.
        """
        if event_type not in {"Yahrzeit", "Birthday", "Anniversary"}:
            raise ValueError("event_type must be one of 'Yahrzeit', 'Birthday', or 'Anniversary'")

        self.params[f"y{index}"] = str(year)
        self.params[f"m{index}"] = str(month)
        self.params[f"d{index}"] = str(day)
        if after_sunset:
            self.params[f"s{index}"] = "on"
        self.params[f"t{index}"] = event_type
        if name:
            # Encode spaces as '+', leave rest to fetch utility
            self.params[f"n{index}"] = name.replace(" ", "+")
        return self

    def _merge_params(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        merged = self.params.copy()
        if extra:
            for k, v in extra.items():
                if k not in _ALLOWED_PARAMS and not k[0] in {"y", "m", "d", "s", "t", "n"}:
                    raise ValueError(f"Invalid extra parameter: '{k}'")
                merged[k] = v
        return merged

    def get_yahrzeit(self, extra: Optional[Dict[str, Any]] = None) -> YahrzeitResponse:
        params = self._merge_params(extra)
        logger.debug(f"Fetching Yahrzeit from {self.endpoint} with params {params}")
        data = fetch_sync(self.endpoint, params=params)
        # The API returns a dict, not a list
        return YahrzeitResponse.from_api(data, url=self.endpoint, params=params)

    async def get_yahrzeit_async(self, extra: Optional[Dict[str, Any]] = None) -> YahrzeitResponse:
        params = self._merge_params(extra)
        logger.debug(f"Fetching async Yahrzeit from {self.endpoint} with params {params}")
        data = await fetch_async(self.endpoint, params=params)
        return YahrzeitResponse.from_api(data, url=self.endpoint, params=params)