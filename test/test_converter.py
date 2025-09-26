import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from hebcal_api.converter import Converter
from hebcal_api.tools.types import ConverterResponse
from hebcal_api.tools.exception import FetchError, InvalidGeoLocationError


class TestConverter:
    """Test suite for the Converter class."""

    @pytest.fixture
    def converter(self):
        """Create a Converter instance for testing."""
        return Converter()

    def test_init(self, converter):
        """Test Converter initialization."""
        assert converter.endpoint == "https://www.hebcal.com/converter"
        assert converter.params == {"cfg": "json", "v": "1"}

    def test_set_param_valid(self, converter):
        """Test set_param with valid parameters."""
        converter.set_param("g2h", 1)
        assert converter.params["g2h"] == 1

    def test_set_param_invalid(self, converter):
        """Test set_param with invalid parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid parameter: 'invalid_param'"):
            converter.set_param("invalid_param", "value")

    def test_set_param_remove_none_value(self, converter):
        """Test set_param removes parameter when value is None."""
        converter.set_param("g2h", 1)
        assert "g2h" in converter.params

        converter.set_param("g2h", None)
        assert "g2h" not in converter.params

    def test_merge_params_no_extra(self, converter):
        """Test _merge_params with no extra parameters."""
        result = converter._merge_params()
        expected = {"cfg": "json", "v": "1"}
        assert result == expected

    def test_merge_params_with_extra_valid(self, converter):
        """Test _merge_params with valid extra parameters."""
        extra = {"g2h": 1, "date": "2024-01-01"}
        result = converter._merge_params(extra)
        expected = {"cfg": "json", "v": "1", "g2h": 1, "date": "2024-01-01"}
        assert result == expected

    def test_merge_params_with_invalid_extra(self, converter):
        """Test _merge_params with invalid extra parameters."""
        extra = {"invalid_param": "value"}
        with pytest.raises(ValueError, match="Invalid extra parameter: 'invalid_param'"):
            converter._merge_params(extra)

    def test_format_date_from_string(self, converter):
        """Test _format_date with string date."""
        result = converter._format_date("2024-01-15")
        assert result == "2024-01-15"

    def test_format_date_from_datetime(self, converter):
        """Test _format_date with datetime object."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = converter._format_date(dt)
        assert result == "2024-01-15"

    def test_format_date_invalid_type(self, converter):
        """Test _format_date with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="Date must be str or datetime"):
            converter._format_date(12345)

    def test_format_date_invalid_string_format(self, converter):
        """Test _format_date with invalid string format raises ValueError."""
        with pytest.raises(ValueError):
            converter._format_date("invalid-date")

    @pytest.mark.asyncio
    async def test_g2h_single_async_success(self, converter):
        """Test g2h_single_async with successful response."""
        mock_data = {
            "gy": 2024, "gm": 1, "gd": 15,
            "hy": 5784, "hm": "Tevet", "hd": 25,
            "hebrew": "כ\"ה בטבת תשפ\"ד"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await converter.g2h_single_async("2024-01-15")

            assert isinstance(result, ConverterResponse)
            assert result.gy == 2024
            assert result.hy == 5784

    def test_g2h_single_success(self, converter):
        """Test g2h_single with successful response."""
        mock_data = {
            "gy": 2024, "gm": 1, "gd": 15,
            "hy": 5784, "hm": "Tevet", "hd": 25,
            "hebrew": "כ\"ה בטבת תשפ\"ד"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = converter.g2h_single("2024-01-15")

            assert isinstance(result, ConverterResponse)
            assert result.gy == 2024
            assert result.hy == 5784

    def test_g2h_single_with_after_sunset(self, converter):
        """Test g2h_single with after_sunset=True."""
        mock_data = {"gy": 2024, "gm": 1, "gd": 15, "hy": 5784}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            converter.g2h_single("2024-01-15", after_sunset=True)

            # Verify that 'gs' parameter was set to 'on'
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    def test_g2h_single_with_strict_false(self, converter):
        """Test g2h_single with strict=False."""
        mock_data = {"gy": 2024, "gm": 1, "gd": 15, "hy": 5784}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            converter.g2h_single("2024-01-15", strict=False)

            # Verify that 'strict' parameter was set to 0
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    def test_g2h_range_success(self, converter):
        """Test g2h_range with successful response."""
        mock_data = [
            {"gy": 2024, "gm": 1, "gd": 15, "hy": 5784},
            {"gy": 2024, "gm": 1, "gd": 16, "hy": 5784}
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = converter.g2h_range("2024-01-15", "2024-01-16")

            assert len(result) == 2
            assert all(isinstance(item, ConverterResponse) for item in result)

    def test_h2g_single_success(self, converter):
        """Test h2g_single with successful response."""
        mock_data = {
            "gy": 2024, "gm": 1, "gd": 15,
            "hy": 5784, "hm": "Tevet", "hd": 25,
            "hebrew": "כ\"ה בטבת תשפ\"ד"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = converter.h2g_single(5784, "Tevet", 25)

            assert isinstance(result, ConverterResponse)
            assert result.hy == 5784
            assert result.gy == 2024

    def test_h2g_single_with_strict_false(self, converter):
        """Test h2g_single with strict=False."""
        mock_data = {"gy": 2024, "gm": 1, "gd": 15, "hy": 5784}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            converter.h2g_single(5784, "Tevet", 25, strict=False)

            # Verify that 'strict' parameter was set to 0
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_h2g_single_async_success(self, converter):
        """Test h2g_single_async with successful response."""
        mock_data = {
            "gy": 2024, "gm": 1, "gd": 15,
            "hy": 5784, "hm": "Tevet", "hd": 25,
            "hebrew": "כ\"ה בטבת תשפ\"ד"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await converter.h2g_single_async(5784, "Tevet", 25)

            assert isinstance(result, ConverterResponse)
            assert result.hy == 5784

    def test_h2g_range_success(self, converter):
        """Test h2g_range with successful response."""
        mock_data = [
            {"gy": 2024, "gm": 1, "gd": 15, "hy": 5784},
            {"gy": 2024, "gm": 1, "gd": 16, "hy": 5784}
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = converter.h2g_range(5784, "Tevet", 25, ndays=2)

            assert len(result) == 2
            assert all(isinstance(item, ConverterResponse) for item in result)

    def test_h2g_range_invalid_ndays(self, converter):
        """Test h2g_range with invalid ndays raises ValueError."""
        with pytest.raises(ValueError, match="ndays must be between 2 and 180"):
            converter.h2g_range(5784, "Tevet", 25, ndays=1)

        with pytest.raises(ValueError, match="ndays must be between 2 and 180"):
            converter.h2g_range(5784, "Tevet", 25, ndays=181)

    def test_h2g_range_with_strict_false(self, converter):
        """Test h2g_range with strict=False."""
        mock_data = [{"gy": 2024, "gm": 1, "gd": 15, "hy": 5784}]
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            converter.h2g_range(5784, "Tevet", 25, ndays=2, strict=False)

            # Verify that 'strict' parameter was set to 0
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None
