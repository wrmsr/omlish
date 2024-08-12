"""
TODO:
 - def maybe(v: lang.Maybe[T])
"""
import collections
import typing as ta


T = ta.TypeVar('T')
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)

Message = str | ta.Callable[..., str | None] | None

_NONE_TYPE = type(None)

_isinstance = isinstance
_issubclass = issubclass
_callable = callable


##


def _default_exception_factory(exc_cls: type[Exception], *args, **kwargs) -> Exception:
    return exc_cls(*args, **kwargs)  # noqa


_EXCEPTION_FACTORY = _default_exception_factory


def _raise(
        exception_type: type[Exception],
        default_message: str,
        message: Message,
        *args: ta.Any,
        **kwargs: ta.Any,
) -> ta.NoReturn:
    if _callable(message):
        message = ta.cast(ta.Callable, message)(*args, **kwargs)
        if _isinstance(message, tuple):
            message, *args = message  # type: ignore
    if message is None:
        message = default_message
    exc = _EXCEPTION_FACTORY(exception_type, message, *args, **kwargs)
    raise exc


##


def _unpack_isinstance_spec(spec: ta.Any) -> tuple:
    if not _isinstance(spec, tuple):
        spec = (spec,)
    if None in spec:
        spec = tuple(filter(None, spec)) + (_NONE_TYPE,)  # noqa
    if ta.Any in spec:
        spec = (object,)
    return spec


def isinstance(v: ta.Any, spec: type[T] | tuple, msg: Message = None) -> T:  # noqa
    if not _isinstance(v, _unpack_isinstance_spec(spec)):
        _raise(TypeError, 'Must be instance', msg, v, spec)
    return v


def of_isinstance(spec: type[T] | tuple, msg: Message = None) -> ta.Callable[[ta.Any], T]:
    def inner(v):
        return isinstance(v, _unpack_isinstance_spec(spec), msg)

    return inner


def cast(v: ta.Any, cls: type[T], msg: Message = None) -> T:  # noqa
    if not _isinstance(v, cls):
        _raise(TypeError, 'Must be instance', msg, v, cls)
    return v


def of_cast(cls: type[T], msg: Message = None) -> ta.Callable[[T], T]:
    def inner(v):
        return isinstance(v, cls, msg)

    return inner


def not_isinstance(v: T, spec: ta.Any, msg: Message = None) -> T:  # noqa
    if _isinstance(v, _unpack_isinstance_spec(spec)):
        _raise(TypeError, 'Must not be instance', msg, v, spec)
    return v


def of_not_isinstance(spec: ta.Any, msg: Message = None) -> ta.Callable[[T], T]:
    def inner(v):
        return not_isinstance(v, _unpack_isinstance_spec(spec), msg)

    return inner


##


def issubclass(v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
    if not _issubclass(v, spec):
        _raise(TypeError, 'Must be subclass', msg, v, spec)
    return v


def not_issubclass(v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
    if _issubclass(v, spec):
        _raise(TypeError, 'Must not be subclass', msg, v, spec)
    return v


##


def in_(v: T, c: ta.Container[T], msg: Message = None) -> T:
    if v not in c:
        _raise(ValueError, 'Must be in', msg, v, c)
    return v


def not_in(v: T, c: ta.Container[T], msg: Message = None) -> T:
    if v in c:
        _raise(ValueError, 'Must not be in', msg, v, c)
    return v


def empty(v: SizedT, msg: Message = None) -> SizedT:
    if len(v) != 0:
        _raise(ValueError, 'Must be empty', msg, v)
    return v


def not_empty(v: SizedT, msg: Message = None) -> SizedT:
    if len(v) == 0:
        _raise(ValueError, 'Must not be empty', msg, v)
    return v


def unique(it: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
    dupes = [e for e, c in collections.Counter(it).items() if c > 1]
    if dupes:
        _raise(ValueError, 'Must be unique', msg, it, dupes)
    return it


def single(obj: ta.Iterable[T], message: Message = None) -> T:
    try:
        [value] = obj
    except ValueError:
        _raise(ValueError, 'Must be single', message, obj)
    else:
        return value


def optional_single(obj: ta.Iterable[T], message: Message = None) -> T | None:
    it = iter(obj)
    try:
        value = next(it)
    except StopIteration:
        return None
    try:
        next(it)
    except StopIteration:
        return value  # noqa
    _raise(ValueError, 'Must be empty or single', message, obj)


##


def none(v: ta.Any, msg: Message = None) -> None:
    if v is not None:
        _raise(ValueError, 'Must be None', msg, v)


def not_none(v: T | None, msg: Message = None) -> T:
    if v is None:
        _raise(ValueError, 'Must not be None', msg, v)
    return v


##


def equal(v: T, *os: ta.Any, msg: Message = None) -> T:
    for o in os:
        if o != v:
            _raise(ValueError, 'Must be equal', msg, v, os)
    return v


def is_(v: T, *os: ta.Any, msg: Message = None) -> T:
    for o in os:
        if o is not v:
            _raise(ValueError, 'Must be the same', msg, v, os)
    return v


def is_not(v: T, *os: ta.Any, msg: Message = None) -> T:
    for o in os:
        if o is v:
            _raise(ValueError, 'Must not be the same', msg, v, os)
    return v


def callable(v: T, msg: Message = None) -> T:  # noqa
    if not _callable(v):
        _raise(TypeError, 'Must be callable', msg, v)
    return v  # type: ignore


def non_empty_str(v: str | None, msg: Message = None) -> str:
    if not _isinstance(v, str) or not v:
        _raise(ValueError, 'Must be non-empty str', msg, v)
    return v


##


def arg(v: bool, msg: Message = None) -> None:
    if not v:
        _raise(RuntimeError, 'Argument condition not met', msg)


def state(v: bool, msg: Message = None) -> None:
    if not v:
        _raise(RuntimeError, 'State condition not met', msg)
