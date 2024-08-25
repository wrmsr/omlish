import typing as ta


class Secret:
    _VALUE_ATTR = '__secret_value__'

    def __init__(self, *, key: str | None, value: str) -> None:
        super().__init__()
        self._key = key
        setattr(self, self._VALUE_ATTR, lambda: value)

    def __repr__(self) -> str:
        return f'Secret<{self._key or ""}>'

    def __str__(self) -> ta.NoReturn:
        raise TypeError

    def reveal(self) -> str:
        return getattr(self, self._VALUE_ATTR)()
