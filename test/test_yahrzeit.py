from unittest.mock import patch

import pytest

from hebcal_api import (
    YahrzeitEventType,
    YahrzeitRequest,
    YahrzeitRequestEvent,
    fetch_yahrzeit,
    fetch_yahrzeit_async,
)
from hebcal_api.utils.types import YahrzeitResponse


class TestYahrzeit:
    """Test suite for the Yahrzeit functional API."""

    @patch("hebcal_api.client.fetch_sync")
    def test_fetch_yahrzeit_basic(self, mock_fetch):
        """Test fetch_yahrzeit with basic parameters."""
        mock_data = {"events": []}
        mock_fetch.return_value = mock_data

        req = YahrzeitRequest(
            events=[
                YahrzeitRequestEvent(
                    year=2020,
                    month=1,
                    day=15,
                    event_type=YahrzeitEventType.YAHRZEIT,
                    name="John Doe",
                )
            ]
        )
        result = fetch_yahrzeit(req)

        assert isinstance(result, YahrzeitResponse)
        mock_fetch.assert_called_once()

    @patch("hebcal_api.client.fetch_async")
    @pytest.mark.asyncio
    async def test_fetch_yahrzeit_async_basic(self, mock_fetch_async):
        """Test fetch_yahrzeit_async with basic parameters."""
        mock_data = {"events": []}
        mock_fetch_async.return_value = mock_data

        req = YahrzeitRequest(
            events=[
                YahrzeitRequestEvent(
                    year=2020,
                    month=1,
                    day=15,
                    event_type=YahrzeitEventType.YAHRZEIT,
                    name="John Doe",
                )
            ]
        )
        result = await fetch_yahrzeit_async(req)

        assert isinstance(result, YahrzeitResponse)
        mock_fetch_async.assert_called_once()
