from unittest.mock import patch

import pytest

from hebcal_api import ZmanimRequest, fetch_zmanim, fetch_zmanim_async
from hebcal_api.utils.types import ZmanimResponse


class TestZmanim:
    """Test suite for the Zmanim functional API."""

    @patch("hebcal_api.client.fetch_sync")
    def test_fetch_zmanim_basic(self, mock_fetch):
        """Test fetch_zmanim with basic parameters."""
        mock_data = {"date": "2024-01-15", "version": "1.0", "location": {}, "times": {}}
        mock_fetch.return_value = mock_data

        req = ZmanimRequest(date="2024-01-15", geonameid=12345)
        result = fetch_zmanim(req)

        assert isinstance(result, ZmanimResponse)
        mock_fetch.assert_called_once()

    @patch("hebcal_api.client.fetch_async")
    @pytest.mark.asyncio
    async def test_fetch_zmanim_async_basic(self, mock_fetch_async):
        """Test fetch_zmanim_async with basic parameters."""
        mock_data = {"date": "2024-01-15", "version": "1.0", "location": {}, "times": {}}
        mock_fetch_async.return_value = mock_data

        req = ZmanimRequest(date="2024-01-15", geonameid=12345)
        result = await fetch_zmanim_async(req)

        assert isinstance(result, ZmanimResponse)
        mock_fetch_async.assert_called_once()
