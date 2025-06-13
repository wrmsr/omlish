"""
While the core functionality lives in `lite/check.py` and is available in lite code, this module re-exports the contents
of its `check` API object as module-globals for convenience. It also sets up some non-lite integration, most notably
`ArgsRenderer` for rendering the AST's and values of failed checks (if the necessary optional dependencies are present).
"""
import typing as ta

from .lite.check import CheckArgsRenderer as ArgsRenderer  # noqa
from .lite.check import CheckExceptionFactory as ExceptionFactory  # noqa
from .lite.check import CheckLateConfigureFn as LateConfigureFn  # noqa
from .lite.check import CheckMessage as Message  # noqa
from .lite.check import CheckOnRaiseFn as OnRaiseFn  # noqa
from .lite.check import Checks
from .lite.check import check


T = ta.TypeVar('T')
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)


_isinstance = isinstance
_issubclass = issubclass
_callable = callable


##


def register_on_raise(fn: OnRaiseFn) -> None:
    check.register_on_raise(fn)


def unregister_on_raise(fn: OnRaiseFn) -> None:
    check.unregister_on_raise(fn)


##


def _try_get_args_rendering() -> ArgsRenderer | None:
    try:
        from .diag.asts import ArgsRenderer

        ArgsRenderer.smoketest()

    except Exception:  # noqa
        return None

    def _real_render_args(fmt: str, *args: ta.Any) -> str | None:
        ra = ArgsRenderer(back=3).render_args(*args)
        if ra is None:
            return None

        return fmt % tuple(str(a) for a in ra)

    return _real_render_args


def _try_enable_args_rendering(c: Checks) -> None:
    if (rf := _try_get_args_rendering()) is not None:
        c.set_args_renderer(rf)


check.register_late_configure(_try_enable_args_rendering)


##
# The following code manually proxies to the lite code, as opposed to simply assigning global names to instance methods
# of `check`, to assist type analysis in tools - pycharm for example has a hard time deducing the return types in such
# cases. The functions are however dynamically overwritten below with direct references to the method to remove one
# layer of call indirection at runtime.


_CHECK_PROXY_FUNCTIONS: dict[str, ta.Any] = {}


def _check_proxy_function(fn: T) -> T:
    name = fn.__name__  # type: ignore[attr-defined]
    if name in _CHECK_PROXY_FUNCTIONS:
        raise NameError(fn)
    _CHECK_PROXY_FUNCTIONS[name] = fn
    return fn


##


@ta.overload
def isinstance(v: ta.Any, spec: type[T], msg: Message = None) -> T:  # noqa
    ...


@ta.overload
def isinstance(v: ta.Any, spec: ta.Any, msg: Message = None) -> ta.Any:  # noqa
    ...


@_check_proxy_function
def isinstance(v, spec, msg=None):  # noqa
    return check.isinstance(v, spec, msg=msg)


@ta.overload
def of_isinstance(spec: type[T], msg: Message = None) -> ta.Callable[[ta.Any], T]:
    ...


@ta.overload
def of_isinstance(spec: ta.Any, msg: Message = None) -> ta.Callable[[ta.Any], ta.Any]:
    ...


@_check_proxy_function
def of_isinstance(spec, msg=None):
    return check.of_isinstance(spec, msg=msg)


@_check_proxy_function
def cast(v: ta.Any, cls: type[T], msg: Message = None) -> T:
    return check.cast(v, cls, msg=msg)


@_check_proxy_function
def of_cast(cls: type[T], msg: Message = None) -> ta.Callable[[T], T]:
    return check.of_cast(cls, msg=msg)


@_check_proxy_function
def not_isinstance(v: T, spec: ta.Any, msg: Message = None) -> T:
    return check.not_isinstance(v, spec, msg=msg)


@_check_proxy_function
def of_not_isinstance(spec: ta.Any, msg: Message = None) -> ta.Callable[[T], T]:
    return check.of_not_isinstance(spec, msg=msg)


#


@_check_proxy_function
def issubclass(v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:  # noqa
    return check.issubclass(v, spec, msg=msg)


@_check_proxy_function
def not_issubclass(v: type[T], spec: ta.Any, msg: Message = None) -> type[T]:
    return check.not_issubclass(v, spec, msg=msg)


#


@_check_proxy_function
def in_(v: T, c: ta.Container[T], msg: Message = None) -> T:
    return check.in_(v, c, msg=msg)


@_check_proxy_function
def not_in(v: T, c: ta.Container[T], msg: Message = None) -> T:
    return check.not_in(v, c, msg=msg)


@_check_proxy_function
def empty(v: SizedT, msg: Message = None) -> SizedT:
    return check.empty(v, msg=msg)


@_check_proxy_function
def iterempty(v: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
    return check.iterempty(v, msg=msg)


@_check_proxy_function
def not_empty(v: SizedT, msg: Message = None) -> SizedT:
    return check.not_empty(v, msg=msg)


@_check_proxy_function
def unique(it: ta.Iterable[T], msg: Message = None) -> ta.Iterable[T]:
    return check.unique(it, msg=msg)


@_check_proxy_function
def single(obj: ta.Iterable[T], msg: Message = None) -> T:
    return check.single(obj, msg=msg)


@_check_proxy_function
def opt_single(obj: ta.Iterable[T], msg: Message = None) -> T | None:
    return check.opt_single(obj, msg=msg)


#


@_check_proxy_function
def none(v: ta.Any, msg: Message = None) -> None:
    return check.none(v, msg=msg)


@_check_proxy_function
def not_none(v: T | None, msg: Message = None) -> T:
    return check.not_none(v, msg=msg)


#


@_check_proxy_function
def equal(v: T, o: ta.Any, msg: Message = None) -> T:
    return check.equal(v, o, msg=msg)


@_check_proxy_function
def not_equal(v: T, o: ta.Any, msg: Message = None) -> T:
    return check.not_equal(v, o, msg=msg)


@_check_proxy_function
def is_(v: T, o: ta.Any, msg: Message = None) -> T:
    return check.is_(v, o, msg=msg)


@_check_proxy_function
def is_not(v: T, o: ta.Any, msg: Message = None) -> T:
    return check.is_not(v, o, msg=msg)


@_check_proxy_function
def callable(v: T, msg: Message = None) -> T:  # noqa
    return check.callable(v, msg=msg)


@_check_proxy_function
def non_empty_str(v: str | None, msg: Message = None) -> str:
    return check.non_empty_str(v, msg=msg)


@_check_proxy_function
def replacing(expected: ta.Any, old: ta.Any, new: T, msg: Message = None) -> T:
    return check.replacing(expected, old, new, msg=msg)


@_check_proxy_function
def replacing_none(old: ta.Any, new: T, msg: Message = None) -> T:
    return check.replacing_none(old, new, msg=msg)


#


@_check_proxy_function
def arg(v: bool, msg: Message = None) -> None:
    return check.arg(v, msg=msg)


@_check_proxy_function
def state(v: bool, msg: Message = None) -> None:
    return check.state(v, msg=msg)


##


def _install_direct_check_proxy_functions() -> None:
    for n in _CHECK_PROXY_FUNCTIONS:
        globals()[n] = getattr(check, n)


_install_direct_check_proxy_functions()
