import typing as ta


T = ta.TypeVar('T')

_NONE_TYPE = type(None)

_isinstance = isinstance
_issubclass = issubclass
_callable = callable


##


def _raise(o):
    raise o


##


def _unpack_isinstance_spec(spec: ta.Any) -> tuple:
    if not _isinstance(spec, tuple):
        spec = (spec,)
    if None in spec:
        spec = tuple(filter(None, spec)) + (_NONE_TYPE,)  # type: ignore
    if ta.Any in spec:
        spec = (object,)
    return spec


def isinstance(v: T, spec: ta.Any) -> T:  # noqa
    if not _isinstance(v, _unpack_isinstance_spec(spec)):
        _raise(TypeError(v))
    return v


def of_isinstance(spec: ta.Any) -> ta.Callable[[T], T]:
    def inner(v):
        return isinstance(v, _unpack_isinstance_spec(spec))

    return inner


def not_isinstance(v: T, spec: ta.Any) -> T:  # noqa
    if _isinstance(v, _unpack_isinstance_spec(spec)):
        _raise(TypeError(v, spec))
    return v


def of_not_isinstance(spec: ta.Any) -> ta.Callable[[T], T]:
    def inner(v):
        return not_isinstance(v, _unpack_isinstance_spec(spec))

    return inner


##


def issubclass(v: ta.Type[T], spec: ta.Any) -> ta.Type[T]:  # noqa
    if not _issubclass(v, spec):
        _raise(TypeError(v))
    return v


def not_issubclass(v: ta.Type[T], spec: ta.Any) -> ta.Type[T]:  # noqa
    if _issubclass(v, spec):
        _raise(TypeError(v))
    return v


##


def not_none(v: ta.Optional[T]) -> T:
    if v is None:
        _raise(ValueError(v))
    return v  # type: ignore


def callable(v: T) -> T:
    if not _callable(v):
        _raise(TypeError(v))
    return v
