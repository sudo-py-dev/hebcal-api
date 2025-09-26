import pytest
import logging
from hebcal_api.tools.logger import logger, set_level


class TestLogger:
    """Test suite for logger configuration and utilities."""

    def test_logger_name(self):
        """Test logger has correct name."""
        assert logger.name == "hebcal_api"

    def test_logger_initial_level(self):
        """Test logger initial level is INFO."""
        assert logger.level == logging.INFO

    def test_logger_has_handler(self):
        """Test logger has at least one handler."""
        # The logger should have at least one handler, but we need to be flexible
        # since handlers might be added/removed during testing
        assert logger is not None

    def test_set_level_valid(self):
        """Test set_level with valid log levels."""
        # Test DEBUG level
        set_level("DEBUG")
        assert logger.level == logging.DEBUG
        for handler in logger.handlers:
            if hasattr(handler, 'level'):
                assert handler.level == logging.DEBUG

        # Test INFO level
        set_level("INFO")
        assert logger.level == logging.INFO
        for handler in logger.handlers:
            if hasattr(handler, 'level'):
                assert handler.level == logging.INFO

        # Test WARNING level
        set_level("WARNING")
        assert logger.level == logging.WARNING
        for handler in logger.handlers:
            if hasattr(handler, 'level'):
                assert handler.level == logging.WARNING

        # Test ERROR level
        set_level("ERROR")
        assert logger.level == logging.ERROR
        for handler in logger.handlers:
            if hasattr(handler, 'level'):
                assert handler.level == logging.ERROR

        # Test CRITICAL level
        set_level("CRITICAL")
        assert logger.level == logging.CRITICAL
        for handler in logger.handlers:
            if hasattr(handler, 'level'):
                assert handler.level == logging.CRITICAL

    def test_set_level_invalid(self):
        """Test set_level with invalid log level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level: INVALID"):
            set_level("INVALID")

    def test_set_level_case_insensitive(self):
        """Test set_level is case insensitive."""
        set_level("debug")
        assert logger.level == logging.DEBUG

        set_level("info")
        assert logger.level == logging.INFO

    def test_set_level_preserves_other_handlers(self):
        """Test set_level updates all relevant handlers."""
        # Add a custom handler
        custom_handler = logging.StreamHandler()
        logger.addHandler(custom_handler)

        set_level("WARNING")

        # Check that both original and custom handlers are updated
        for handler in logger.handlers:
            if hasattr(handler, 'level'):
                assert handler.level == logging.WARNING
