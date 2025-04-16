import dataclasses as dc
import typing as ta

from ... import check


T = ta.TypeVar('T')


##


class field_modifier:  # noqa
    def __init__(self, fn: ta.Callable[[dc.Field], dc.Field]) -> None:
        super().__init__()
        self.fn = fn

    def __ror__(self, other: T) -> T:
        return self(other)

    def __call__(self, f: T) -> T:
        return check.isinstance(self.fn(check.isinstance(f, dc.Field)), dc.Field)  # type: ignore


##


def update_fields(
        fn: ta.Callable[[str, dc.Field], dc.Field],
        fields: ta.Iterable[str] | None = None,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(cls):
        if fields is None:
            for a, v in list(cls.__dict__.items()):
                if isinstance(v, dc.Field):
                    setattr(cls, a, fn(a, v))

        else:
            for a in fields:
                try:
                    v = cls.__dict__[a]
                except KeyError:
                    v = dc.field()
                else:
                    if not isinstance(v, dc.Field):
                        v = dc.field(default=v)
                setattr(cls, a, fn(a, v))

        return cls

    check.not_isinstance(fields, str)
    return inner
