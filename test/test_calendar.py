from unittest.mock import patch

import pytest

from hebcal_api import CalendarRequest, fetch_calendar, fetch_calendar_async
from hebcal_api.utils.types import CalendarResponse


class TestCalendar:
    """Test suite for the Calendar functional API."""

    @patch("hebcal_api.client.fetch_sync")
    def test_fetch_calendar_basic(self, mock_fetch):
        """Test fetch_calendar with basic parameters."""
        mock_data = {"title": "Test", "items": [], "date": "2024-01-15T00:00:00Z"}
        mock_fetch.return_value = mock_data

        req = CalendarRequest(year=2024, geonameid=12345)
        result = fetch_calendar(req)

        assert isinstance(result, CalendarResponse)
        mock_fetch.assert_called_once()

    @patch("hebcal_api.client.fetch_async")
    @pytest.mark.asyncio
    async def test_fetch_calendar_async_basic(self, mock_fetch_async):
        """Test fetch_calendar_async with basic parameters."""
        mock_data = {"title": "Test Async", "items": [], "date": "2024-01-15T00:00:00Z"}
        mock_fetch_async.return_value = mock_data

        req = CalendarRequest(year=2024, geonameid=12345)
        result = await fetch_calendar_async(req)

        assert isinstance(result, CalendarResponse)
        assert result.title == "Test Async"
        mock_fetch_async.assert_called_once()
