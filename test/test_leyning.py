from unittest.mock import patch

import pytest

from hebcal_api import LeyningRequest, LeyningResponse, fetch_leyning, fetch_leyning_async


class TestLeyning:
    """Test suite for the Leyning functional API."""

    @patch("hebcal_api.client.fetch_sync")
    def test_fetch_leyning_basic(self, mock_fetch):
        """Test fetch_leyning with basic parameters."""
        mock_data = {
            "date": "2024-01-15",
            "items": [],
            "location": "Test",
            "range": {"start": "2024-01-15", "end": "2024-01-15"},
        }
        mock_fetch.return_value = mock_data

        req = LeyningRequest(date="2024-01-15")
        result = fetch_leyning(req)

        assert isinstance(result, LeyningResponse)
        mock_fetch.assert_called_once()

    @patch("hebcal_api.client.fetch_async")
    @pytest.mark.asyncio
    async def test_fetch_leyning_async_basic(self, mock_fetch_async):
        """Test fetch_leyning_async with basic parameters."""
        mock_data = {
            "date": "2024-01-15",
            "items": [],
            "location": "Test",
            "range": {"start": "2024-01-15", "end": "2024-01-15"},
        }
        mock_fetch_async.return_value = mock_data

        req = LeyningRequest(date="2024-01-15")
        result = await fetch_leyning_async(req)

        assert isinstance(result, LeyningResponse)
        mock_fetch_async.assert_called_once()
