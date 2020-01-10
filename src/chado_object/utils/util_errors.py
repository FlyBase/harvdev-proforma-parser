
class CodingError(Exception):
    """Exception raised for errors that should not happen really.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.error = message
