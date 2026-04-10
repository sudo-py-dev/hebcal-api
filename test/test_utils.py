from unittest.mock import MagicMock, patch

import pytest

from hebcal_api.exceptions import HebcalValidationError
from hebcal_api.utils.utils import fetch_async, fetch_sync, remove_hebrew_nikud


class TestUtils:
    """Test suite for utility functions."""

    @patch("httpx.Client")
    def test_fetch_sync_success(self, mock_client_class):
        """Test fetch_sync with a successful response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.url = "http://example.com"
        mock_client.get.return_value = mock_response

        mock_client_class.return_value.__enter__.return_value = mock_client

        result = fetch_sync("http://example.com", params={"key": "value"})

        assert result == {"status": "success"}
        mock_client.get.assert_called_once_with("http://example.com", params={"key": "value"})

    @patch("httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_fetch_async_success(self, mock_client_class):
        """Test fetch_async with a successful response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.url = "http://example.com"

        # Async mock setup
        async def mock_get(*args, **kwargs):
            return mock_response

        mock_client.get = mock_get
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await fetch_async("http://example.com", params={"key": "value"})

        assert result == {"status": "success"}

    def test_remove_hebrew_nikud(self):
        """Test removing Hebrew nikud."""
        assert remove_hebrew_nikud("שָׁלוֹם") == "שלום"
        assert remove_hebrew_nikud("יִשְׂרָאֵל") == "ישראל"

    def test_remove_hebrew_nikud_empty(self):
        with pytest.raises(HebcalValidationError):
            remove_hebrew_nikud("")
