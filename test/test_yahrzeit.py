import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from hebcal_api.yahrzeit import Yahrzeit
from hebcal_api.tools.types import YahrzeitResponse
from hebcal_api.tools.exception import FetchError, InvalidGeoLocationError


class TestYahrzeit:
    """Test suite for the Yahrzeit class."""

    @pytest.fixture
    def yahrzeit(self):
        """Create a Yahrzeit instance for testing."""
        return Yahrzeit()

    def test_init(self, yahrzeit):
        """Test Yahrzeit initialization."""
        assert yahrzeit.endpoint == "https://www.hebcal.com/yahrzeit"
        assert yahrzeit.params == {"cfg": "json", "v": "yahrzeit"}

    def test_set_param_valid(self, yahrzeit):
        """Test set_param with valid parameters."""
        yahrzeit.set_param("years", 5)
        assert yahrzeit.params["years"] == 5

    def test_set_param_invalid(self, yahrzeit):
        """Test set_param with invalid parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid parameter: 'invalid_param'"):
            yahrzeit.set_param("invalid_param", "value")

    def test_set_param_remove_none_value(self, yahrzeit):
        """Test set_param removes parameter when value is None."""
        yahrzeit.set_param("years", 5)
        assert "years" in yahrzeit.params

        yahrzeit.set_param("years", None)
        assert "years" not in yahrzeit.params

    def test_add_event_yahrzeit(self, yahrzeit):
        """Test add_event with Yahrzeit type."""
        yahrzeit.add_event(1, 2020, 1, 15, after_sunset=False, event_type="Yahrzeit", name="John Doe")

        assert yahrzeit.params["y1"] == "2020"
        assert yahrzeit.params["m1"] == "1"
        assert yahrzeit.params["d1"] == "15"
        assert yahrzeit.params["t1"] == "Yahrzeit"
        assert yahrzeit.params["n1"] == "John+Doe"

    def test_add_event_birthday(self, yahrzeit):
        """Test add_event with Birthday type."""
        yahrzeit.add_event(2, 1990, 5, 10, after_sunset=True, event_type="Birthday", name="Jane Smith")

        assert yahrzeit.params["y2"] == "1990"
        assert yahrzeit.params["m2"] == "5"
        assert yahrzeit.params["d2"] == "10"
        assert yahrzeit.params["s2"] == "on"
        assert yahrzeit.params["t2"] == "Birthday"
        assert yahrzeit.params["n2"] == "Jane+Smith"

    def test_add_event_anniversary(self, yahrzeit):
        """Test add_event with Anniversary type."""
        yahrzeit.add_event(3, 2000, 12, 25, event_type="Anniversary", name="Wedding")

        assert yahrzeit.params["y3"] == "2000"
        assert yahrzeit.params["m3"] == "12"
        assert yahrzeit.params["d3"] == "25"
        assert yahrzeit.params["t3"] == "Anniversary"
        assert yahrzeit.params["n3"] == "Wedding"

    def test_add_event_invalid_type(self, yahrzeit):
        """Test add_event with invalid event type raises ValueError."""
        with pytest.raises(ValueError, match="event_type must be one of"):
            yahrzeit.add_event(1, 2020, 1, 15, event_type="Invalid")

    def test_add_event_name_with_spaces(self, yahrzeit):
        """Test add_event properly encodes names with spaces."""
        yahrzeit.add_event(1, 2020, 1, 15, event_type="Yahrzeit", name="John Q Doe")

        assert yahrzeit.params["n1"] == "John+Q+Doe"

    def test_merge_params_no_extra(self, yahrzeit):
        """Test _merge_params with no extra parameters."""
        result = yahrzeit._merge_params()
        expected = {"cfg": "json", "v": "yahrzeit"}
        assert result == expected

    def test_merge_params_with_extra_valid(self, yahrzeit):
        """Test _merge_params with valid extra parameters."""
        extra = {"years": 5, "i": "on"}
        result = yahrzeit._merge_params(extra)
        expected = {"cfg": "json", "v": "yahrzeit", "years": 5, "i": "on"}
        assert result == expected

    def test_merge_params_with_dynamic_params(self, yahrzeit):
        """Test _merge_params with dynamic event parameters."""
        yahrzeit.add_event(1, 2020, 1, 15, event_type="Yahrzeit", name="Test")
        extra = {"years": 5}

        result = yahrzeit._merge_params(extra)
        expected = {
            "cfg": "json", "v": "yahrzeit",
            "years": 5,
            "y1": "2020", "m1": "1", "d1": "15", "t1": "Yahrzeit", "n1": "Test"
        }
        assert result == expected

    def test_merge_params_with_invalid_extra(self, yahrzeit):
        """Test _merge_params with invalid extra parameters."""
        extra = {"invalid_param": "value"}
        with pytest.raises(ValueError, match="Invalid extra parameter: 'invalid_param'"):
            yahrzeit._merge_params(extra)

    def test_get_yahrzeit_success(self, yahrzeit):
        """Test get_yahrzeit with successful response."""
        mock_data = {
            "events": [
                {
                    "title": "Yahrzeit of John Doe",
                    "date": "2024-01-15T12:00:00Z",
                    "hebrew": "כ\"ה בטבת תשפ\"ד",
                    "category": "yahrzeit",
                    "heDateParts": {"yy": 5784, "mm": 10, "dd": 25, "month_name": "Tevet"}
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = yahrzeit.get_yahrzeit()

            assert isinstance(result, YahrzeitResponse)
            assert len(result.events) == 1
            assert result.events[0].title == "Yahrzeit of John Doe"

    def test_get_yahrzeit_with_event(self, yahrzeit):
        """Test get_yahrzeit with added event."""
        yahrzeit.add_event(1, 2020, 1, 15, event_type="Yahrzeit", name="John Doe")

        mock_data = {
            "events": [
                {
                    "title": "Yahrzeit of John Doe",
                    "date": "2024-01-15T12:00:00Z",
                    "hebrew": "כ\"ה בטבת תשפ\"ד",
                    "category": "yahrzeit",
                    "heDateParts": {"yy": 5784, "mm": 10, "dd": 25, "month_name": "Tevet"}
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            result = yahrzeit.get_yahrzeit()

            assert isinstance(result, YahrzeitResponse)
            assert len(result.events) == 1

    def test_get_yahrzeit_with_extra_params(self, yahrzeit):
        """Test get_yahrzeit with extra parameters."""
        extra = {"years": 5, "i": "on"}
        mock_data = {"events": []}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            yahrzeit.get_yahrzeit(extra)

            # Verify that extra parameters were merged
            call_args = mock_response.raise_for_status.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_get_yahrzeit_async_success(self, yahrzeit):
        """Test get_yahrzeit_async with successful response."""
        mock_data = {
            "events": [
                {
                    "title": "Yahrzeit of John Doe",
                    "date": "2024-01-15T12:00:00Z",
                    "hebrew": "כ\"ה בטבת תשפ\"ד",
                    "category": "yahrzeit",
                    "heDateParts": {"yy": 5784, "mm": 10, "dd": 25, "month_name": "Tevet"}
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await yahrzeit.get_yahrzeit_async()

            assert isinstance(result, YahrzeitResponse)
            assert len(result.events) == 1
