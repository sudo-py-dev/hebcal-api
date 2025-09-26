import logging

# Module-level logger for the library
logger = logging.getLogger("hebcal_api")
logger.setLevel(logging.INFO)

# Console handler
_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_ch.setFormatter(formatter)


if not logger.hasHandlers():
    logger.addHandler(_ch)

# -------------------------------
# Helper functions for users
# -------------------------------

def set_level(level: str):
    """
    Set the logging level for the library.

    Args:
        level (str): One of "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logger.setLevel(numeric_level)
    _ch.setLevel(numeric_level)
    # Update all handlers to maintain consistency
    for handler in logger.handlers:
        handler.setLevel(numeric_level)