class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidationError(Error):
    """Exception raised for errors in the input.

    """
