class FetchError(Exception):
    """Custom exception for fetch errors in hebcal_api."""
    pass

class ParseError(Exception):
    """Custom exception for parse errors in hebcal_api."""
    pass


class InvalidGeoLocationError(Exception):
    """Custom exception for invalid geo location errors in hebcal_api."""
    pass
    