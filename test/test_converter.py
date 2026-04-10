from unittest.mock import patch

import pytest

from hebcal_api import ConverterRequest, fetch_converter, fetch_converter_async
from hebcal_api.utils.types import ConverterResponse


class TestConverter:
    """Test suite for the Converter functional API."""

    @patch("hebcal_api.converter.fetch_sync")
    def test_fetch_converter_g2h_single(self, mock_fetch):
        """Test fetch_converter for single g2h conversion."""
        mock_data = {
            "gy": 2024,
            "gm": 1,
            "gd": 15,
            "hy": 5784,
            "hm": "Tevet",
            "hd": 25,
            "hebrew": 'כ"ה בטבת תשפ"ד',
            "date": "2024-01-15T00:00:00Z",
        }
        mock_fetch.return_value = mock_data

        req = ConverterRequest(date="2024-01-15", conversion_type="g2h")
        result = fetch_converter(req)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ConverterResponse)
        assert result[0].hy == 5784

    @patch("hebcal_api.converter.fetch_async")
    @pytest.mark.asyncio
    async def test_fetch_converter_async_g2h_single(self, mock_fetch_async):
        """Test fetch_converter_async for single g2h conversion."""
        mock_data = {
            "gy": 2024,
            "gm": 1,
            "gd": 15,
            "hy": 5784,
            "hm": "Tevet",
            "hd": 25,
            "hebrew": 'כ"ה בטבת תשפ"ד',
            "date": "2024-01-15T00:00:00Z",
        }
        mock_fetch_async.return_value = mock_data

        req = ConverterRequest(date="2024-01-15", conversion_type="g2h")
        result = await fetch_converter_async(req)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].hy == 5784
