import typing as ta


##


class YamlError(Exception):
    def __init__(self, message: ta.Union[str, Exception], *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(message, *args, **kwargs)

        self.message = message
