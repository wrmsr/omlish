class CheckError(Exception):
    pass


class FieldCheckError(CheckError):
    def __init__(self, field: str) -> None:
        super().__init__(field)
        self.field = field
