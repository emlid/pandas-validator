
class ValidationError(Exception):
    """An error while validating data."""
    def __init__(self, message, error_type, column=None, rows=None):
        super(ValidationError, self).__init__(message)

        self.message = message
        self.error_type = error_type
        self.column = column
        self.rows = rows
