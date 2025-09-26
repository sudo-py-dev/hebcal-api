import pytest
from hebcal_api.tools.exception import FetchError, ParseError, InvalidGeoLocationError


class TestExceptions:
    """Test suite for custom exception classes."""

    def test_fetch_error_is_exception(self):
        """Test FetchError is a proper Exception subclass."""
        assert issubclass(FetchError, Exception)

    def test_parse_error_is_exception(self):
        """Test ParseError is a proper Exception subclass."""
        assert issubclass(ParseError, Exception)

    def test_invalid_geo_location_error_is_exception(self):
        """Test InvalidGeoLocationError is a proper Exception subclass."""
        assert issubclass(InvalidGeoLocationError, Exception)

    def test_fetch_error_can_be_raised(self):
        """Test FetchError can be raised and caught."""
        with pytest.raises(FetchError):
            raise FetchError("Test fetch error")

    def test_parse_error_can_be_raised(self):
        """Test ParseError can be raised and caught."""
        with pytest.raises(ParseError):
            raise ParseError("Test parse error")

    def test_invalid_geo_location_error_can_be_raised(self):
        """Test InvalidGeoLocationError can be raised and caught."""
        with pytest.raises(InvalidGeoLocationError):
            raise InvalidGeoLocationError("Test geo location error")

    def test_fetch_error_message(self):
        """Test FetchError preserves error message."""
        error_message = "HTTP request failed"
        with pytest.raises(FetchError, match=error_message):
            raise FetchError(error_message)

    def test_parse_error_message(self):
        """Test ParseError preserves error message."""
        error_message = "JSON parsing failed"
        with pytest.raises(ParseError, match=error_message):
            raise ParseError(error_message)

    def test_invalid_geo_location_error_message(self):
        """Test InvalidGeoLocationError preserves error message."""
        error_message = "Invalid geographic location"
        with pytest.raises(InvalidGeoLocationError, match=error_message):
            raise InvalidGeoLocationError(error_message)
