
class BasicValidationError(Exception):
    """An error while validating data."""
    def __init__(self, message):
        super(BasicValidationError, self).__init__(message)

        self.message = message


class ValidationError(BasicValidationError):
    """An error while validating data."""
    def __init__(self, message, error_type, column, rows=None):
        super(ValidationError, self).__init__(message)

        self.error_type = error_type
        self.column = column
        self.rows = rows
