# ruff: noqa: UP007 UP045
import typing as ta


##


class Secret:
    __sensitive__ = True

    _VALUE_ATTR = '__secret_value__'

    def __init__(self, *, key: ta.Optional[str] = None, value: str) -> None:
        super().__init__()
        self._key = key
        setattr(self, self._VALUE_ATTR, lambda: value)

    def __repr__(self) -> str:
        return f'Secret<{self._key or ""}>'

    def __str__(self) -> ta.NoReturn:
        raise TypeError

    def reveal(self) -> str:
        return getattr(self, self._VALUE_ATTR)()

    #

    def __reduce__(self) -> ta.NoReturn:
        raise TypeError

    def __reduce_ex__(self, protocol) -> ta.NoReturn:
        raise TypeError

    def __getstate__(self) -> ta.NoReturn:
        raise TypeError

    def __setstate__(self, state) -> ta.NoReturn:
        raise TypeError
