import typing as ta

from .. import lang


T = ta.TypeVar('T')


##


@ta.final
class _AutoValue(lang.Final, ta.Generic[T]):
    def __init__(self, *, _cls: type[T] | None = None) -> None:
        self._cls = _cls

    def __repr__(self) -> str:
        return f'orm.auto_value{f"[{self._cls.__name__}]" if self._cls is not None else ""}@{id(self):x}'

    def __bool__(self) -> ta.NoReturn:
        raise TypeError(self)


class _AutoValueFactory:
    def __getitem__(self, cls: type[T]) -> ta.Callable[[], T]:
        return lambda: _AutoValue(_cls=cls)  # type: ignore[return-value]

    def __call__(self) -> ta.Callable[[], ta.Any]:
        return lambda: _AutoValue()


auto_value = _AutoValueFactory()  # noqa


_VALUE_TYPES: tuple[type, ...] = (
    _AutoValue,
)
