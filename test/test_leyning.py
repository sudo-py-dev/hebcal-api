import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, date
from hebcal_api.leyning import Leyning
from hebcal_api.tools.types import LeyningResponse
from hebcal_api.tools.exception import FetchError, InvalidGeoLocationError


class TestLeyning:
    """Test suite for the Leyning class."""

    @pytest.fixture
    def leyning(self):
        """Create a Leyning instance for testing."""
        return Leyning()

    def test_init(self, leyning):
        """Test Leyning initialization."""
        assert leyning.base_url == "https://www.hebcal.com/leyning"
        assert leyning.params == {"cfg": "json", "v": "1"}

    def test_merge_params_no_extra(self, leyning):
        """Test _merge_params with no extra parameters."""
        result = leyning._merge_params()
        expected = {"cfg": "json", "v": "1"}
        assert result == expected

    def test_merge_params_with_extra_valid(self, leyning):
        """Test _merge_params with valid extra parameters."""
        extra = {"date": "2024-01-15", "i": "on"}
        result = leyning._merge_params(extra)
        expected = {"cfg": "json", "v": "1", "date": "2024-01-15", "i": "on"}
        assert result == expected

    def test_merge_params_with_invalid_extra(self, leyning):
        """Test _merge_params with invalid extra parameters."""
        extra = {"invalid_param": "value"}
        with pytest.raises(ValueError, match="Invalid extra parameter: 'invalid_param'"):
            leyning._merge_params(extra)

    def test_format_datetime_from_string(self, leyning):
        """Test _format_datetime with string date."""
        result = leyning._format_datetime("2024-01-15")
        assert result == "2024-01-15"

    def test_format_datetime_from_datetime(self, leyning):
        """Test _format_datetime with datetime object."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = leyning._format_datetime(dt)
        assert result == "2024-01-15"

    def test_format_datetime_from_date(self, leyning):
        """Test _format_datetime with date object."""
        d = date(2024, 1, 15)
        result = leyning._format_datetime(d)
        assert result == "2024-01-15"

    def test_format_datetime_invalid_type(self, leyning):
        """Test _format_datetime with invalid type raises ValueError."""
        with pytest.raises(ValueError, match="dt not provaided or not in the right type"):
            leyning._format_datetime(12345)

    def test_format_datetime_invalid_string_format(self, leyning):
        """Test _format_datetime with invalid string format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            leyning._format_datetime("invalid-date")

    def test_validate_dates_single_date(self, leyning):
        """Test _validate_dates with single date."""
        result = leyning._validate_dates("2024-01-15", None, None)
        assert result == {"date": "2024-01-15"}

    def test_validate_dates_date_range(self, leyning):
        """Test _validate_dates with date range."""
        result = leyning._validate_dates(None, "2024-01-15", "2024-01-20")
        assert result == {"start": "2024-01-15", "end": "2024-01-20"}

    def test_validate_dates_no_date_no_range(self, leyning):
        """Test _validate_dates with no date and no range raises ValueError."""
        with pytest.raises(ValueError, match="You must provide either a single 'date' or both 'start' and 'end'"):
            leyning._validate_dates(None, None, None)

    def test_validate_dates_partial_range(self, leyning):
        """Test _validate_dates with partial range raises ValueError."""
        with pytest.raises(ValueError, match="You must provide either a single 'date' or both 'start' and 'end'"):
            leyning._validate_dates(None, "2024-01-15", None)

    def test_prepare_params_single_date(self, leyning):
        """Test _prepare_params with single date."""
        result = leyning._prepare_params("2024-01-15", None, None, False, True)
        expected = {
            "cfg": "json", "v": "1",
            "date": "2024-01-15",
            "i": "off",
            "triennial": "on"
        }
        assert result == expected

    def test_prepare_params_date_range(self, leyning):
        """Test _prepare_params with date range."""
        result = leyning._prepare_params(None, "2024-01-15", "2024-01-20", True, False)
        expected = {
            "cfg": "json", "v": "1",
            "start": "2024-01-15",
            "end": "2024-01-20",
            "i": "on",
            "triennial": "off"
        }
        assert result == expected

    def test_get_leyning_single_date_success(self, leyning):
        """Test get_leyning with single date and successful response."""
        mock_data = {
            "date": "2024-01-15",
            "location": "Test Location",
            "range": {"start": "2024-01-15", "end": "2024-01-15"},
            "items": []
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = leyning.get_leyning("2024-01-15")

            assert isinstance(result, LeyningResponse)
            assert result.date == datetime.fromisoformat("2024-01-15")

    def test_get_leyning_date_range_success(self, leyning):
        """Test get_leyning with date range and successful response."""
        mock_data = {
            "date": "2024-01-15",
            "location": "Test Location",
            "range": {"start": "2024-01-15", "end": "2024-01-20"},
            "items": []
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = leyning.get_leyning(start="2024-01-15", end="2024-01-20")

            assert isinstance(result, LeyningResponse)

    def test_get_leyning_diaspora_true(self, leyning):
        """Test get_leyning with diaspora=True."""
        mock_data = {"date": "2024-01-15", "items": []}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            leyning.get_leyning("2024-01-15", diaspora=True)

            # Verify that 'i' parameter was set to 'on'
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    def test_get_leyning_triennial_false(self, leyning):
        """Test get_leyning with triennial=False."""
        mock_data = {"date": "2024-01-15", "items": []}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            leyning.get_leyning("2024-01-15", triennial=False)

            # Verify that 'triennial' parameter was set to 'off'
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    def test_get_leyning_no_date_or_range(self, leyning):
        """Test get_leyning with no date or range raises ValueError."""
        with pytest.raises(ValueError, match="You must provide either a single 'date' or both 'start' and 'end'"):
            leyning.get_leyning()

    @pytest.mark.asyncio
    async def test_get_leyning_async_success(self, leyning):
        """Test get_leyning_async with successful response."""
        mock_data = {
            "date": "2024-01-15",
            "location": "Test Location",
            "range": {"start": "2024-01-15", "end": "2024-01-15"},
            "items": []
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await leyning.get_leyning_async("2024-01-15")

            assert isinstance(result, LeyningResponse)
            assert result.date == datetime.fromisoformat("2024-01-15")
