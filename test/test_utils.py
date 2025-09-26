import pytest
import httpx
import requests
from unittest.mock import patch, MagicMock
from hebcal_api.tools.utils import fetch_async, fetch_sync, remove_hebrew_nikud
from hebcal_api.tools.exception import FetchError, InvalidGeoLocationError


class TestUtils:
    """Test suite for utility functions."""

    @pytest.mark.asyncio
    async def test_fetch_async_success(self):
        """Test fetch_async with successful response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await fetch_async("https://example.com")

            assert result == {"test": "data"}
            mock_client.return_value.__aenter__.return_value.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_async_with_params(self):
        """Test fetch_async with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.url = "https://example.com?param=value"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await fetch_async("https://example.com", params={"param": "value"})

            assert result == {"test": "data"}

    @pytest.mark.asyncio
    async def test_fetch_async_http_error(self):
        """Test fetch_async with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=mock_response
        )

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            with pytest.raises(FetchError):
                await fetch_async("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_async_invalid_geo_location(self):
        """Test fetch_async with invalid geo location error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "can't find geonameid 123"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=mock_response
        )

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            with pytest.raises(InvalidGeoLocationError):
                await fetch_async("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_async_request_error(self):
        """Test fetch_async with request error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")

            with pytest.raises(FetchError):
                await fetch_async("https://example.com")

    def test_fetch_sync_success(self):
        """Test fetch_sync with successful response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = fetch_sync("https://example.com")

            assert result == {"test": "data"}

    def test_fetch_sync_with_params(self):
        """Test fetch_sync with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.url = "https://example.com?param=value"
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = fetch_sync("https://example.com", params={"param": "value"})

            assert result == {"test": "data"}

    def test_fetch_sync_http_error(self):
        """Test fetch_sync with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_response.request = MagicMock()
        mock_response.request.url = "https://example.com"
        mock_response.url = "https://example.com"
        
        # Create a proper HTTPError with request
        http_error = requests.HTTPError("404 Client Error")
        http_error.request = mock_response.request

        with patch('requests.get', return_value=mock_response):
            with pytest.raises(FetchError):
                fetch_sync("https://example.com")

    def test_fetch_sync_invalid_geo_location(self):
        """Test fetch_sync with invalid geo location error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "can't find geonameid 123"}
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_response.request = MagicMock()
        mock_response.request.url = "https://example.com"
        mock_response.url = "https://example.com"
        
        # Create a proper HTTPError with request and response
        http_error = requests.HTTPError("404 Client Error")
        http_error.request = mock_response.request
        http_error.response = mock_response

        with patch('requests.get', return_value=mock_response):
            with pytest.raises(FetchError):
                fetch_sync("https://example.com")

    def test_fetch_sync_request_error(self):
        """Test fetch_sync with request error."""
        with patch('requests.get', side_effect=requests.RequestException("Connection failed")):
            with pytest.raises(FetchError):
                fetch_sync("https://example.com")

    def test_remove_hebrew_nikud_basic(self):
        """Test remove_hebrew_nikud with basic Hebrew text."""
        text = "שָׁלוֹם"
        result = remove_hebrew_nikud(text)
        assert result == "שלום"

    def test_remove_hebrew_nikud_with_nikud(self):
        """Test remove_hebrew_nikud with various nikud."""
        text = "בְּרֵאשִׁית"
        result = remove_hebrew_nikud(text)
        assert result == "בראשית"

    def test_remove_hebrew_nikud_mixed_text(self):
        """Test remove_hebrew_nikud with mixed Hebrew and other text."""
        text = "Hello בְּרֵאשִׁית world"
        result = remove_hebrew_nikud(text)
        assert result == "Hello בראשית world"

    def test_remove_hebrew_nikud_no_nikud(self):
        """Test remove_hebrew_nikud with text that has no nikud."""
        text = "שלום"
        result = remove_hebrew_nikud(text)
        assert result == "שלום"

    def test_remove_hebrew_nikud_empty_string(self):
        """Test remove_hebrew_nikud with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be None"):
            remove_hebrew_nikud("")

    def test_remove_hebrew_nikud_none_input(self):
        """Test remove_hebrew_nikud with None input raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be None"):
            remove_hebrew_nikud(None)
