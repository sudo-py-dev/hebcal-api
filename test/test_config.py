from src.hebcal_api.config import BASE_URL, DEFAULT_PARAMS


class TestConfig:
    """Test suite for config constants."""

    def test_base_url(self):
        """Test BASE_URL constant."""
        assert BASE_URL == "https://www.hebcal.com"

    def test_default_params(self):
        """Test DEFAULT_PARAMS constant."""
        expected_params = {
            "v": "1",
            "cfg": "json",
        }
        assert DEFAULT_PARAMS == expected_params

    def test_default_params_structure(self):
        """Test DEFAULT_PARAMS has required structure."""
        assert "v" in DEFAULT_PARAMS
        assert "cfg" in DEFAULT_PARAMS
        assert DEFAULT_PARAMS["v"] == "1"
        assert DEFAULT_PARAMS["cfg"] == "json"
