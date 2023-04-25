import typing as ta


T = ta.TypeVar('T')

_isinstance = isinstance


def _raise(o):
    raise o


def isinstance(v: T, ty: ta.Any) -> T:  # noqa
    if not _isinstance(v, ty):
        _raise(TypeError(v, ty))
    return v


def not_isinstance(v: T, ty: ta.Any) -> T:  # noqa
    if _isinstance(v, ty):
        _raise(TypeError(v, ty))
    return v


def not_none(v: ta.Optional[T]) -> T:
    if v is None:
        _raise(ValueError(v))
    return v  # type: ignore
