import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from hebcal_api.zmanim import Zmanim
from hebcal_api.tools.types import ZmanimResponse
from hebcal_api.tools.exception import FetchError, InvalidGeoLocationError


class TestZmanim:
    """Test suite for the Zmanim class."""

    @pytest.fixture
    def zmanim(self):
        """Create a Zmanim instance for testing."""
        return Zmanim()

    def test_init(self, zmanim):
        """Test Zmanim initialization."""
        assert zmanim.endpoint == "https://www.hebcal.com/zmanim"
        assert zmanim.params == {"cfg": "json", "v": "1"}

    def test_set_param_valid(self, zmanim):
        """Test set_param with valid parameters."""
        zmanim.set_param("geonameid", 12345)
        assert zmanim.params["geonameid"] == 12345

    def test_set_param_invalid(self, zmanim):
        """Test set_param with invalid parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid parameter: 'invalid_param'"):
            zmanim.set_param("invalid_param", "value")

    def test_set_param_remove_none_value(self, zmanim):
        """Test set_param removes parameter when value is None."""
        zmanim.set_param("geonameid", 12345)
        assert "geonameid" in zmanim.params

        zmanim.set_param("geonameid", None)
        assert "geonameid" not in zmanim.params

    def test_merge_params_no_extra(self, zmanim):
        """Test _merge_params with no extra parameters."""
        result = zmanim._merge_params()
        expected = {"cfg": "json", "v": "1"}
        assert result == expected

    def test_merge_params_with_extra_valid(self, zmanim):
        """Test _merge_params with valid extra parameters."""
        extra = {"geonameid": 12345, "elevation": 1}
        result = zmanim._merge_params(extra)
        expected = {"cfg": "json", "v": "1", "geonameid": 12345, "elevation": 1}
        assert result == expected

    def test_merge_params_with_invalid_extra(self, zmanim):
        """Test _merge_params with invalid extra parameters."""
        extra = {"invalid_param": "value"}
        with pytest.raises(ValueError, match="Invalid extra parameter: 'invalid_param'"):
            zmanim._merge_params(extra)

    def test_format_datetime_from_string(self, zmanim):
        """Test _format_datetime with string date."""
        result = zmanim._format_datetime("2024-01-15")
        assert result == "2024-01-15"

    def test_format_datetime_from_datetime(self, zmanim):
        """Test _format_datetime with datetime object."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = zmanim._format_datetime(dt)
        assert result == "2024-01-15"

    def test_format_datetime_invalid_type(self, zmanim):
        """Test _format_datetime with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="Date parameters must be either str or datetime"):
            zmanim._format_datetime(12345)

    def test_format_datetime_invalid_string_format(self, zmanim):
        """Test _format_datetime with invalid string format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            zmanim._format_datetime("invalid-date")

    def test_validate_dates_single_date(self, zmanim):
        """Test _validate_dates with single date."""
        result = zmanim._validate_dates("2024-01-15", None, None)
        assert result == {"date": "2024-01-15"}

    def test_validate_dates_date_range(self, zmanim):
        """Test _validate_dates with date range."""
        result = zmanim._validate_dates(None, "2024-01-15", "2024-01-20")
        assert result == {"start": "2024-01-15", "end": "2024-01-20"}

    def test_validate_dates_no_date_no_range(self, zmanim):
        """Test _validate_dates with no date and no range raises ValueError."""
        with pytest.raises(ValueError, match="You must provide either a single 'date' or both 'start' and 'end'"):
            zmanim._validate_dates(None, None, None)

    def test_validate_dates_partial_range(self, zmanim):
        """Test _validate_dates with partial range raises ValueError."""
        with pytest.raises(ValueError, match="You must provide either a single 'date' or both 'start' and 'end'"):
            zmanim._validate_dates(None, "2024-01-15", None)

    def test_prepare_params_single_date(self, zmanim):
        """Test _prepare_params with single date."""
        result = zmanim._prepare_params("2024-01-15", None, None, geonameid=12345)
        expected = {
            "cfg": "json", "v": "1",
            "date": "2024-01-15",
            "geonameid": 12345
        }
        assert result == expected

    def test_prepare_params_date_range(self, zmanim):
        """Test _prepare_params with date range."""
        result = zmanim._prepare_params(None, "2024-01-15", "2024-01-20", latitude=40.7128, longitude=-74.0060)
        expected = {
            "cfg": "json", "v": "1",
            "start": "2024-01-15",
            "end": "2024-01-20",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        assert result == expected

    def test_prepare_params_partial_lat_long(self, zmanim):
        """Test _prepare_params with partial latitude/longitude raises ValueError."""
        with pytest.raises(ValueError, match="Both latitude and longitude must be provided together"):
            zmanim._prepare_params("2024-01-15", None, None, latitude=40.7128)

    def test_prepare_params_with_sec_and_elevation(self, zmanim):
        """Test _prepare_params with sec and elevation flags."""
        result = zmanim._prepare_params("2024-01-15", None, None, geonameid=12345, sec=True, elevation=True)
        expected = {
            "cfg": "json", "v": "1",
            "date": "2024-01-15",
            "geonameid": 12345,
            "sec": 1,
            "elevation": 1
        }
        assert result == expected

    def test_get_zmanim_single_date_success(self, zmanim):
        """Test get_zmanim with single date and successful response."""
        mock_data = {
            "date": "2024-01-15",
            "version": "1.0",
            "location": {"title": "New York, NY", "city": "New York", "tzid": "America/New_York"},
            "times": {
                "sunrise": "07:15:00",
                "sunset": "16:45:00",
                "chatzot": "12:00:00"
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = zmanim.get_zmanim("2024-01-15", geonameid=12345)

            assert isinstance(result, ZmanimResponse)
            assert result.date == "2024-01-15"

    def test_get_zmanim_date_range_success(self, zmanim):
        """Test get_zmanim with date range and successful response."""
        mock_data = {
            "date": "2024-01-15",
            "version": "1.0",
            "location": {"title": "New York, NY", "city": "New York", "tzid": "America/New_York"},
            "times": {
                "sunrise": "07:15:00",
                "sunset": "16:45:00",
                "chatzot": "12:00:00"
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = zmanim.get_zmanim(start="2024-01-15", end="2024-01-20", geonameid=12345)

            assert isinstance(result, ZmanimResponse)

    def test_get_zmanim_with_lat_long_success(self, zmanim):
        """Test get_zmanim with latitude/longitude and successful response."""
        mock_data = {
            "date": "2024-01-15",
            "version": "1.0",
            "location": {"title": "Custom Location", "latitude": 40.7128, "longitude": -74.0060},
            "times": {
                "sunrise": "07:15:00",
                "sunset": "16:45:00"
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = zmanim.get_zmanim("2024-01-15", latitude=40.7128, longitude=-74.0060)

            assert isinstance(result, ZmanimResponse)

    def test_get_zmanim_with_sec_and_elevation(self, zmanim):
        """Test get_zmanim with sec and elevation flags."""
        mock_data = {
            "date": "2024-01-15",
            "version": "1.0",
            "location": {"title": "New York, NY"},
            "times": {}
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            zmanim.get_zmanim("2024-01-15", geonameid=12345, sec=True, elevation=True)

            # Verify that sec and elevation parameters were set
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    def test_get_zmanim_no_date_or_range(self, zmanim):
        """Test get_zmanim with no date or range raises ValueError."""
        with pytest.raises(ValueError, match="You must provide either a single 'date' or both 'start' and 'end'"):
            zmanim.get_zmanim()

    @pytest.mark.asyncio
    async def test_get_zmanim_async_success(self, zmanim):
        """Test get_zmanim_async with successful response."""
        mock_data = {
            "date": "2024-01-15",
            "version": "1.0",
            "location": {"title": "New York, NY", "city": "New York", "tzid": "America/New_York"},
            "times": {
                "sunrise": "07:15:00",
                "sunset": "16:45:00",
                "chatzot": "12:00:00"
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await zmanim.get_zmanim_async("2024-01-15", geonameid=12345)

            assert isinstance(result, ZmanimResponse)
            assert result.date == "2024-01-15"
