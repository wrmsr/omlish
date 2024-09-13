"""
TODO:
 - def maybe(v: lang.Maybe[T])
"""
import collections
import threading
import typing as ta


T = ta.TypeVar('T')
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)

Message: ta.TypeAlias = str | ta.Callable[..., str | None] | None

_NONE_TYPE = type(None)

_isinstance = isinstance
_issubclass = issubclass
_callable = callable


##


_CONFIG_LOCK = threading.RLock()


OnRaiseFn: ta.TypeAlias = ta.Callable[[Exception], None]
_ON_RAISE: ta.Sequence[OnRaiseFn] = []


def register_on_raise(fn: OnRaiseFn) -> None:
    global _ON_RAISE
    with _CONFIG_LOCK:
        _ON_RAISE = [*_ON_RAISE, fn]


def unregister_on_raise(fn: OnRaiseFn) -> None:
    global _ON_RAISE
    with _CONFIG_LOCK:
        _ON_RAISE = [e for e in _ON_RAISE if e != fn]


#


_render_args: ta.Callable[..., str | None] | None = None


def enable_args_rendering() -> bool:
    global _render_args
    if _render_args is not None:
        return True

    with _CONFIG_LOCK:
        if _render_args is not None:
            return True  # type: ignore

        try:
            from .diag.asts import ArgsRenderer

            ArgsRenderer.smoketest()

        except Exception:  # noqa
            return False

        def _real_render_args(fmt: str, *args: ta.Any) -> str | None:
            ra = ArgsRenderer(back=3).render_args(*args)
            if ra is None:
                return None

            return fmt % tuple(str(a) for a in ra)

        _render_args = _real_render_args
        return True


enable_args_rendering()


#


def _default_exception_factory(exc_cls: type[Exception], *args, **kwargs) -> Exception:
    return exc_cls(*args, **kwargs)  # noqa


_EXCEPTION_FACTORY = _default_exception_factory


class _Args:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def _raise(
        exception_type: type[Exception],
        default_message: str,
        message: Message,
        ak: _Args = _Args(),
        *,
        render_fmt: str | None = None,
) -> ta.NoReturn:
    exc_args = ()
    if _callable(message):
        message = ta.cast(ta.Callable, message)(*ak.args, **ak.kwargs)
        if _isinstance(message, tuple):
            message, *exc_args = message  # type: ignore

    if message is None:
        message = default_message

    if render_fmt is not None and _render_args is not None:
        rendered_args = _render_args(render_fmt, *ak.args)
        if rendered_args is not None:
            message = f'{message} : {rendered_args}'

    exc = _EXCEPTION_FACTORY(
        exception_type,
        message,
        *exc_args,
        *ak.args,
        **ak.kwargs,
    )

    for fn in _ON_RAISE:
        fn(exc)

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
        _raise(
            TypeError,
            'Must be instance',
            msg,
            _Args(v, spec),
            render_fmt='not isinstance(%s, %s)',
        )

    return v


def of_isinstance(spec: type[T] | tuple, msg: Message = None) -> ta.Callable[[ta.Any], T]:
    def inner(v):
        return isinstance(v, _unpack_isinstance_spec(spec), msg)

    return inner


def cast(v: ta.Any, cls: type[T], msg: Message = None) -> T:  # noqa
    if not _isinstance(v, cls):
        _raise(
            TypeError,
            'Must be instance',
            msg,
            _Args(v, cls),
        )

    return v


def of_cast(cls: type[T], msg: Message = None) -> ta.Callable[[T], T]:
    def inner(v):
        return isinstance(v, cls, msg)

    return inner


def not_isinstance(v: T, spec: ta.Any, msg: Message = None) -> T:  # noqa
    if _isinstance(v, _unpack_isinstance_spec(spec)):
        _raise(
            TypeError,
            'Must not be instance',
            msg,
            _Args(v, spec),
            render_fmt='isinstance(%s, %s)',
        )

    return v


def of_not_isinstance(spec: ta.Any, msg: Message = None) -> ta.Callable[[T], T]:
    def inner(v):
        return not_isinstance(v, _unpack_isinstance_spec(spec), msg)

    return inner


##


def issubclass(v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
    if not _issubclass(v, spec):
        _raise(
            TypeError,
            'Must be subclass',
            msg,
            _Args(v, spec),
            render_fmt='not issubclass(%s, %s)',
        )

    return v


def not_issubclass(v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
    if _issubclass(v, spec):
        _raise(
            TypeError,
            'Must not be subclass',
            msg,
            _Args(v, spec),
            render_fmt='issubclass(%s, %s)',
        )

    return v


##


def in_(v: T, c: ta.Container[T], msg: Message = None) -> T:
    if v not in c:
        _raise(
            ValueError,
            'Must be in',
            msg,
            _Args(v, c),
            render_fmt='%s not in %s',
        )

    return v


def not_in(v: T, c: ta.Container[T], msg: Message = None) -> T:
    if v in c:
        _raise(
            ValueError,
            'Must not be in',
            msg,
            _Args(v, c),
            render_fmt='%s in %s',
        )

    return v


def empty(v: SizedT, msg: Message = None) -> SizedT:
    if len(v) != 0:
        _raise(
            ValueError,
            'Must be empty',
            msg,
            _Args(v),
            render_fmt='%s',
        )

    return v


def iterempty(v: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
    it = iter(v)
    try:
        next(it)
    except StopIteration:
        pass
    else:
        _raise(
            ValueError,
            'Must be empty',
            msg,
            _Args(v),
            render_fmt='%s',
        )

    return v


def not_empty(v: SizedT, msg: Message = None) -> SizedT:
    if len(v) == 0:
        _raise(
            ValueError,
            'Must not be empty',
            msg,
            _Args(v),
            render_fmt='%s',
        )

    return v


def unique(it: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
    dupes = [e for e, c in collections.Counter(it).items() if c > 1]
    if dupes:
        _raise(
            ValueError,
            'Must be unique',
            msg,
            _Args(it, dupes),
        )

    return it


def single(obj: ta.Iterable[T], message: Message = None) -> T:
    try:
        [value] = obj
    except ValueError:
        _raise(
            ValueError,
            'Must be single',
            message,
            _Args(obj),
            render_fmt='%s',
        )

    return value


def opt_single(obj: ta.Iterable[T], message: Message = None) -> T | None:
    it = iter(obj)
    try:
        value = next(it)
    except StopIteration:
        return None

    try:
        next(it)
    except StopIteration:
        return value  # noqa

    _raise(
        ValueError,
        'Must be empty or single',
        message,
        _Args(obj),
        render_fmt='%s',
    )


##


def none(v: ta.Any, msg: Message = None) -> None:
    if v is not None:
        _raise(
            ValueError,
            'Must be None',
            msg,
            _Args(v),
            render_fmt='%s',
        )


def not_none(v: T | None, msg: Message = None) -> T:
    if v is None:
        _raise(
            ValueError,
            'Must not be None',
            msg,
            _Args(v),
            render_fmt='%s',
        )

    return v


##


def equal(v: T, o: ta.Any, msg: Message = None) -> T:
    if o != v:
        _raise(
            ValueError,
            'Must be equal',
            msg,
            _Args(v, o),
            render_fmt='%s != %s',
        )

    return v


def is_(v: T, o: ta.Any, msg: Message = None) -> T:
    if o is not v:
        _raise(
            ValueError,
            'Must be the same',
            msg,
            _Args(v, o),
            render_fmt='%s is not %s',
        )

    return v


def is_not(v: T, o: ta.Any, msg: Message = None) -> T:
    if o is v:
        _raise(
            ValueError,
            'Must not be the same',
            msg,
            _Args(v, o),
            render_fmt='%s is %s',
        )

    return v


def callable(v: T, msg: Message = None) -> T:  # noqa
    if not _callable(v):
        _raise(
            TypeError,
            'Must be callable',
            msg,
            _Args(v),
            render_fmt='%s',
        )

    return v  # type: ignore


def non_empty_str(v: str | None, msg: Message = None) -> str:
    if not _isinstance(v, str) or not v:
        _raise(
            ValueError,
            'Must be non-empty str',
            msg,
            _Args(v),
            render_fmt='%s',
        )

    return v


def replacing(expected: ta.Any, old: ta.Any, new: T, msg: Message = None) -> T:
    if old != expected:
        _raise(
            ValueError,
            'Must be replacing',
            msg,
            _Args(expected, old, new),
            render_fmt='%s -> %s -> %s',
        )

    return new


def replacing_none(old: ta.Any, new: T, msg: Message = None) -> T:
    if old is not None:
        _raise(
            ValueError,
            'Must be replacing None',
            msg,
            _Args(old, new),
            render_fmt='%s -> %s',
        )

    return new


##


def arg(v: bool, msg: Message = None) -> None:
    if not v:
        _raise(
            RuntimeError,
            'Argument condition not met',
            msg,
            _Args(v),
            render_fmt='%s',
        )


def state(v: bool, msg: Message = None) -> None:
    if not v:
        _raise(
            RuntimeError,
            'State condition not met',
            msg,
            _Args(v),
            render_fmt='%s',
        )
