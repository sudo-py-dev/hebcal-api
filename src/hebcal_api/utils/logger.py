from loguru import logger

logger.disable("hebcal_api")


def set_level(level: str) -> None:
    """
    Enable logging for the hebcal-api library and set the minimum level.
    Note: For complete control, configure loguru directly in your application.
    """
    logger.enable("hebcal_api")
