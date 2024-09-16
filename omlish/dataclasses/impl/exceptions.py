class ValidationError(Exception):
    pass


class FieldValidationError(ValidationError):
    def __init__(self, field: str) -> None:
        super().__init__(field)
        self.field = field
