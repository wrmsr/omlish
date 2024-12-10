"""
TODO:
 - def maybe(v: lang.Maybe[T])
 - patch / override lite.check ?
  - checker interface?
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


_ARGS_RENDERER: ta.Callable[..., str | None] | None = None


def _try_enable_args_rendering() -> bool:
    global _ARGS_RENDERER
    if _ARGS_RENDERER is not None:
        return True

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

    _ARGS_RENDERER = _real_render_args
    return True


_TRIED_ENABLED_ARGS_RENDERING: bool | None = None


def try_enable_args_rendering() -> bool:
    global _TRIED_ENABLED_ARGS_RENDERING
    if _TRIED_ENABLED_ARGS_RENDERING is not None:
        return _TRIED_ENABLED_ARGS_RENDERING

    with _CONFIG_LOCK:
        if _TRIED_ENABLED_ARGS_RENDERING is None:
            _TRIED_ENABLED_ARGS_RENDERING = _try_enable_args_rendering()

        return _TRIED_ENABLED_ARGS_RENDERING


##


def _default_exception_factory(exc_cls: type[Exception], *args, **kwargs) -> Exception:
    return exc_cls(*args, **kwargs)  # noqa


_EXCEPTION_FACTORY = _default_exception_factory


class _ArgsKwargs:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


##


class Checks:
    def _raise(
            self,
            exception_type: type[Exception],
            default_message: str,
            message: Message,
            ak: _ArgsKwargs = _ArgsKwargs(),
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

        try_enable_args_rendering()

        if render_fmt is not None and _ARGS_RENDERER is not None:
            rendered_args = _ARGS_RENDERER(render_fmt, *ak.args)
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

    #

    def _unpack_isinstance_spec(self, spec: ta.Any) -> tuple:
        if isinstance(spec, type):
            return (spec,)
        if not isinstance(spec, tuple):
            spec = (spec,)
        if None in spec:
            spec = tuple(filter(None, spec)) + (_NONE_TYPE,)  # noqa
        if ta.Any in spec:
            spec = (object,)
        return spec

    def isinstance(self, v: ta.Any, spec: type[T] | tuple, msg: Message = None) -> T:  # noqa
        if not isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                _ArgsKwargs(v, spec),
                render_fmt='not isinstance(%s, %s)',
            )

        return v

    def of_isinstance(self, spec: type[T] | tuple, msg: Message = None) -> ta.Callable[[ta.Any], T]:
        def inner(v):
            return isinstance(v, self._unpack_isinstance_spec(spec), msg)

        return inner

    def cast(self, v: ta.Any, cls: type[T], msg: Message = None) -> T:  # noqa
        if not isinstance(v, cls):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                _ArgsKwargs(v, cls),
            )

        return v

    def of_cast(self, cls: type[T], msg: Message = None) -> ta.Callable[[T], T]:
        def inner(v):
            return isinstance(v, cls, msg)

        return inner

    def not_isinstance(self, v: T, spec: ta.Any, msg: Message = None) -> T:  # noqa
        if _isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                _ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: Message = None) -> ta.Callable[[T], T]:
        def inner(v):
            return self.not_isinstance(v, self._unpack_isinstance_spec(spec), msg)

        return inner

    ##

    def issubclass(self, v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
        if not issubclass(v, spec):
            self._raise(
                TypeError,
                'Must be subclass',
                msg,
                _ArgsKwargs(v, spec),
                render_fmt='not issubclass(%s, %s)',
            )

        return v

    def not_issubclass(self, v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
        if issubclass(v, spec):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                _ArgsKwargs(v, spec),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    ##

    def in_(self, v: T, c: ta.Container[T], msg: Message = None) -> T:
        if v not in c:
            self._raise(
                ValueError,
                'Must be in',
                msg,
                _ArgsKwargs(v, c),
                render_fmt='%s not in %s',
            )

        return v

    def not_in(self, v: T, c: ta.Container[T], msg: Message = None) -> T:
        if v in c:
            self._raise(
                ValueError,
                'Must not be in',
                msg,
                _ArgsKwargs(v, c),
                render_fmt='%s in %s',
            )

        return v

    def empty(self, v: SizedT, msg: Message = None) -> SizedT:
        if len(v) != 0:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def iterempty(self, v: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
        it = iter(v)
        try:
            next(it)
        except StopIteration:
            pass
        else:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def not_empty(self, v: SizedT, msg: Message = None) -> SizedT:
        if len(v) == 0:
            self._raise(
                ValueError,
                'Must not be empty',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def unique(self, it: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
        dupes = [e for e, c in collections.Counter(it).items() if c > 1]
        if dupes:
            self._raise(
                ValueError,
                'Must be unique',
                msg,
                _ArgsKwargs(it, dupes),
            )

        return it

    def single(self, obj: ta.Iterable[T], message: Message = None) -> T:
        try:
            [value] = obj
        except ValueError:
            self._raise(
                ValueError,
                'Must be single',
                message,
                _ArgsKwargs(obj),
                render_fmt='%s',
            )

        return value

    def opt_single(self, obj: ta.Iterable[T], message: Message = None) -> T | None:
        it = iter(obj)
        try:
            value = next(it)
        except StopIteration:
            return None

        try:
            next(it)
        except StopIteration:
            return value  # noqa

        self._raise(
            ValueError,
            'Must be empty or single',
            message,
            _ArgsKwargs(obj),
            render_fmt='%s',
        )

    ##

    def none(self, v: ta.Any, msg: Message = None) -> None:
        if v is not None:
            self._raise(
                ValueError,
                'Must be None',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

    def not_none(self, v: T | None, msg: Message = None) -> T:
        if v is None:
            self._raise(
                ValueError,
                'Must not be None',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    ##

    def equal(self, v: T, o: ta.Any, msg: Message = None) -> T:
        if o != v:
            self._raise(
                ValueError,
                'Must be equal',
                msg,
                _ArgsKwargs(v, o),
                render_fmt='%s != %s',
            )

        return v

    def is_(self, v: T, o: ta.Any, msg: Message = None) -> T:
        if o is not v:
            self._raise(
                ValueError,
                'Must be the same',
                msg,
                _ArgsKwargs(v, o),
                render_fmt='%s is not %s',
            )

        return v

    def is_not(self, v: T, o: ta.Any, msg: Message = None) -> T:
        if o is v:
            self._raise(
                ValueError,
                'Must not be the same',
                msg,
                _ArgsKwargs(v, o),
                render_fmt='%s is %s',
            )

        return v

    def callable(self, v: T, msg: Message = None) -> T:  # noqa
        if not _callable(v):
            self._raise(
                TypeError,
                'Must be callable',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

        return v  # type: ignore

    def non_empty_str(self, v: str | None, msg: Message = None) -> str:
        if not isinstance(v, str) or not v:
            self._raise(
                ValueError,
                'Must be non-empty str',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def replacing(self, expected: ta.Any, old: ta.Any, new: T, msg: Message = None) -> T:
        if old != expected:
            self._raise(
                ValueError,
                'Must be replacing',
                msg,
                _ArgsKwargs(expected, old, new),
                render_fmt='%s -> %s -> %s',
            )

        return new

    def replacing_none(self, old: ta.Any, new: T, msg: Message = None) -> T:
        if old is not None:
            self._raise(
                ValueError,
                'Must be replacing None',
                msg,
                _ArgsKwargs(old, new),
                render_fmt='%s -> %s',
            )

        return new

    ##

    def arg(self, v: bool, msg: Message = None) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'Argument condition not met',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )

    def state(self, v: bool, msg: Message = None) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                _ArgsKwargs(v),
                render_fmt='%s',
            )
