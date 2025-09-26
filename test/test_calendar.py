import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, date
import json
from typing import Dict, Any

from hebcal_api import Calendar
from hebcal_api.tools.types import CalendarResponse
from hebcal_api.tools.exception import FetchError, InvalidGeoLocationError


class TestCalendar:
    """Test suite for the Calendar class."""

    @pytest.fixture
    def calendar(self):
        """Create a Calendar instance for testing."""
        return Calendar()

    def test_init(self, calendar):
        """Test Calendar initialization."""
        assert calendar.endpoint == "https://www.hebcal.com/hebcal"
        assert calendar.params == {"cfg": "json", "v": "1"}

    def test_merge_params_no_extra(self, calendar):
        """Test _merge_params with no extra parameters."""
        result = calendar._merge_params()
        expected = {"cfg": "json", "v": "1"}
        assert result == expected

    def test_merge_params_with_extra_valid(self, calendar):
        """Test _merge_params with valid extra parameters."""
        extra = {"year": 2024, "month": 1}
        result = calendar._merge_params(extra)
        expected = {"cfg": "json", "v": "1", "year": 2024, "month": 1}
        assert result == expected

    def test_merge_params_with_invalid_extra(self, calendar):
        """Test _merge_params with invalid extra parameters."""
        extra = {"invalid_param": "value"}
        with pytest.raises(ValueError, match="Invalid extra parameter: 'invalid_param'"):
            calendar._merge_params(extra)

    def test_format_datetime_from_datetime(self, calendar):
        """Test _format_datetime with datetime object."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = calendar._format_datetime(dt)
        assert result == "2024-01-15"

    def test_format_datetime_from_date(self, calendar):
        """Test _format_datetime with date object."""
        d = date(2024, 1, 15)
        result = calendar._format_datetime(d)
        assert result == "2024-01-15"

    def test_format_datetime_from_string(self, calendar):
        """Test _format_datetime with valid string."""
        dt_str = "2024-01-15"
        result = calendar._format_datetime(dt_str)
        assert result == "2024-01-15"

    def test_format_datetime_invalid_string(self, calendar):
        """Test _format_datetime with invalid string format."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            calendar._format_datetime("15-01-2024")

    def test_format_datetime_invalid_type(self, calendar):
        """Test _format_datetime with invalid type."""
        with pytest.raises(ValueError, match="dt not provaided or not in the right type"):
            calendar._format_datetime(12345)

    def test_validate_date_params_year_only(self, calendar):
        """Test _validate_date_params with year only."""
        result = calendar._validate_date_params(year=2024)
        assert result == {"year": 2024}

    def test_validate_date_params_year_with_month(self, calendar):
        """Test _validate_date_params with year and month."""
        result = calendar._validate_date_params(year=2024, month=1)
        assert result == {"year": 2024, "month": 1}

    def test_validate_date_params_year_with_invalid_month(self, calendar):
        """Test _validate_date_params with invalid month."""
        with pytest.raises(ValueError, match="month must be 'x' or 1-12"):
            calendar._validate_date_params(year=2024, month=13)

    def test_validate_date_params_year_with_number_of_years(self, calendar):
        """Test _validate_date_params with number of years."""
        result = calendar._validate_date_params(year=2024, number_of_years=2)
        assert result == {"year": 2024, "ny": 2}

    def test_validate_date_params_year_with_invalid_ny(self, calendar):
        """Test _validate_date_params with invalid number of years."""
        with pytest.raises(ValueError, match="ny must be >= 1"):
            calendar._validate_date_params(year=2024, number_of_years=0)

    def test_validate_date_params_year_with_year_type(self, calendar):
        """Test _validate_date_params with year type."""
        result = calendar._validate_date_params(year=2024, year_type="H")
        assert result == {"year": 2024, "yt": "H"}

    def test_validate_date_params_invalid_year_type(self, calendar):
        """Test _validate_date_params with invalid year type."""
        with pytest.raises(ValueError, match="yt must be 'G' or 'H'"):
            calendar._validate_date_params(year=2024, year_type="X")

    def test_validate_date_params_start_end(self, calendar):
        """Test _validate_date_params with start and end dates."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        result = calendar._validate_date_params(start=start, end=end)
        assert result == {"start": "2024-01-01", "end": "2024-01-31"}

    def test_validate_date_params_year_and_start_end_conflict(self, calendar):
        """Test _validate_date_params with conflicting parameters."""
        with pytest.raises(ValueError, match="Cannot specify both 'year' and 'start/end'"):
            calendar._validate_date_params(year=2024, start=datetime(2024, 1, 1), end=datetime(2024, 1, 31))

    def test_validate_date_params_no_params(self, calendar):
        """Test _validate_date_params with no parameters."""
        with pytest.raises(ValueError, match="Provide either 'start' and 'end'"):
            calendar._validate_date_params()

    def test_validate_location_params_geonameid(self, calendar):
        """Test _validate_location_params with geonameid."""
        result = calendar._validate_location_params(geonameid=12345)
        assert result == {"geonameid": 12345}

    def test_validate_location_params_invalid_geonameid(self, calendar):
        """Test _validate_location_params with invalid geonameid."""
        with pytest.raises(ValueError, match="geonameid must be a positive integer"):
            calendar._validate_location_params(geonameid=-1)

    def test_validate_location_params_zip_code(self, calendar):
        """Test _validate_location_params with zip code."""
        result = calendar._validate_location_params(zip_code="12345")
        assert result == {"zip": "12345"}

    def test_validate_location_params_invalid_zip_code(self, calendar):
        """Test _validate_location_params with invalid zip code."""
        with pytest.raises(ValueError, match="zip must be a 5-digit string"):
            calendar._validate_location_params(zip_code="1234")

    def test_validate_location_params_latitude_longitude(self, calendar):
        """Test _validate_location_params with latitude and longitude."""
        result = calendar._validate_location_params(latitude=40.7128, longitude=-74.0060, timezone_id="America/New_York")
        assert result == {"latitude": 40.7128, "longitude": -74.0060, "tzid": "America/New_York"}

    def test_validate_location_params_incomplete_lat_lon(self, calendar):
        """Test _validate_location_params with incomplete lat/lon."""
        with pytest.raises(ValueError, match="latitude, longitude, and tzid must all be provided together"):
            calendar._validate_location_params(latitude=40.7128, longitude=-74.0060)

    def test_validate_location_params_city(self, calendar):
        """Test _validate_location_params with city name."""
        result = calendar._validate_location_params(city_name="New York")
        assert result == {"city": "New York"}

    def test_validate_location_params_no_location(self, calendar):
        """Test _validate_location_params with no location."""
        with pytest.raises(ValueError, match="You must provide one location parameter"):
            calendar._validate_location_params()

    def test_validate_location_params_multiple_locations(self, calendar):
        """Test _validate_location_params with multiple locations."""
        with pytest.raises(ValueError, match="Only one location parameter is allowed"):
            calendar._validate_location_params(geonameid=12345, city_name="New York")

    @patch('hebcal_api.calendar.fetch_sync')
    def test_get_calendar_sync_success(self, mock_fetch, calendar):
        """Test _get_calendar_sync with successful response."""
        mock_response = {"title": "Test", "items": []}
        mock_fetch.return_value = mock_response

        result = calendar._get_calendar_sync({"year": 2024})

        assert isinstance(result, CalendarResponse)
        mock_fetch.assert_called_once_with("https://www.hebcal.com/hebcal", params={"cfg": "json", "v": "1", "year": 2024})

    @patch('hebcal_api.calendar.fetch_sync')
    def test_get_calendar_sync_invalid_response_type(self, mock_fetch, calendar):
        """Test _get_calendar_sync with invalid response type."""
        mock_fetch.return_value = "invalid response"

        with pytest.raises(ValueError, match="Invalid response data format"):
            calendar._get_calendar_sync({"year": 2024})

    @patch('hebcal_api.calendar.fetch_async')
    @pytest.mark.asyncio
    async def test_get_calendar_async_success(self, mock_fetch, calendar):
        """Test _get_calendar_async with successful response."""
        mock_response = {"title": "Test", "items": []}
        mock_fetch.return_value = mock_response

        result = await calendar._get_calendar_async({"year": 2024})

        assert isinstance(result, CalendarResponse)
        mock_fetch.assert_called_once_with("https://www.hebcal.com/hebcal", params={"cfg": "json", "v": "1", "year": 2024})

    @patch('hebcal_api.calendar.fetch_async')
    @pytest.mark.asyncio
    async def test_get_calendar_async_invalid_response_type(self, mock_fetch, calendar):
        """Test _get_calendar_async with invalid response type."""
        mock_fetch.return_value = "invalid response"

        with pytest.raises(ValueError, match="Invalid response data format"):
            await calendar._get_calendar_async({"year": 2024})

    @patch.object(Calendar, '_get_calendar_sync')
    def test_get_events_basic(self, mock_get_calendar, calendar):
        """Test get_events with basic parameters."""
        mock_response = MagicMock()
        mock_get_calendar.return_value = mock_response

        result = calendar.get_events(year=2024, geonameid=12345)

        assert result == mock_response
        mock_get_calendar.assert_called_once()

    @patch.object(Calendar, '_get_calendar_async')
    @pytest.mark.asyncio
    async def test_get_events_async_basic(self, mock_get_calendar, calendar):
        """Test get_events_async with basic parameters."""
        mock_response = MagicMock()
        mock_get_calendar.return_value = mock_response

        result = await calendar.get_events_async(year=2024, geonameid=12345)

        assert result == mock_response
        mock_get_calendar.assert_called_once()

    @patch.object(Calendar, '_get_calendar_sync')
    def test_get_events_with_all_params(self, mock_get_calendar, calendar):
        """Test get_events with all possible parameters."""
        mock_response = MagicMock()
        mock_get_calendar.return_value = mock_response

        result = calendar.get_events(
            year=2024,
            year_type="H",
            month=1,
            number_of_years=2,
            geonameid=12345,
            israel_holidays_and_torah_readings=True,
            major_holidays=True,
            yom_tov_only=True,
            minor_holidays=True,
            rosh_chodesh=True,
            minor_fasts=True,
            special_shabbatot=True,
            modern_holidays=True,
            weekly_torah_portion=True,
            include_leyning=True,
            hebrew_date_for_events=True,
            hebrew_date_for_range=True,
            omer_days=True,
            yom_kippur_katan=True,
            molad_dates=True,
            yizkor_dates=True,
            shabbat_mevarchim=True,
            candle_lighting_times=True,
            candle_lighting_minutes_before_sunset=30,
            havdalah_minutes_after_sunset=50,
            havdalah_at_nightfall=True,
            daf_yomi=True,
            daf_a_week=True,
            yerushalmi_yomi_vilna=True,
            yerushalmi_yomi_schottenstein=True,
            mishna_yomi=True,
            nach_yomi=True,
            tanakh_yomi=True,
            daily_tehillim=True,
            daily_rambam_1_chapter=True,
            daily_rambam_3_chapters=True,
            sefer_ha_mitzvot=True,
            kitzur_shulchan_arukh_yomi=True,
            arukh_ha_shulchan_yomi=True,
            sefer_chofetz_chaim=True,
            shemirat_ha_lashon=True,
            pirkei_avot_shabbatot=True,
            holiday_description_only=True,
            language="en"
        )

        assert result == mock_response
        mock_get_calendar.assert_called_once()

    def test_parse_params_method_exists(self, calendar):
        """Test that _parse_params method exists and can be called."""
        # This method is complex and tested indirectly through get_events
        # We just verify it exists and has the right signature
        assert hasattr(calendar, '_parse_params')
        assert callable(calendar._parse_params)
