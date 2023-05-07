"""
TOOD:
 - fuse? usecase: forbid_debug + lock
"""
import collections.abc
import contextlib
import contextvars
import functools
import threading
import types
import typing as ta

from .classes import Protocol


T = ta.TypeVar('T')
IteratorTOrT = ta.Union[ta.Iterator[T], T]
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)
ContextManagedT = ta.TypeVar('ContextManagedT', bound='ContextManaged')
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')


class ContextManaged:

    def __enter__(self: ContextManagedT) -> ContextManagedT:
        return self

    def __exit__(
            self,
            exc_type: ta.Optional[ta.Type[Exception]],
            exc_val: ta.Optional[Exception],
            exc_tb: ta.Optional[types.TracebackType]
    ) -> ta.Optional[bool]:
        return None


class NopContextManaged(ContextManaged):

    def __init_subclass__(cls, **kwargs):
        raise TypeError


NOP_CONTEXT_MANAGED = NopContextManaged()


class NopContextManager:

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def __call__(self, *args, **kwargs):
        return NOP_CONTEXT_MANAGED


nop_context_manager = NOP_CONTEXT_MANAGER = NopContextManager()


class ContextManageable(Protocol, ta.Generic[T]):

    def __enter__(self) -> T:
        raise NotImplementedError

    def __exit__(
            self,
            exc_type: ta.Optional[ta.Type[Exception]],
            exc_val: ta.Optional[Exception],
            exc_tb: ta.Optional[types.TracebackType]
    ) -> ta.Optional[bool]:
        raise NotImplementedError


class ExitStacked:

    @property
    def _exit_stack(self) -> contextlib.ExitStack:
        try:
            return self.__exit_stack  # type: ignore
        except AttributeError:
            es = self.__exit_stack = contextlib.ExitStack()
            return es

    def _enter_context(self, context_manager: ContextManageable[T]) -> T:
        return self._exit_stack.enter_context(ta.cast(ta.ContextManager, context_manager))

    def __enter__(self: ExitStackedT) -> ExitStackedT:
        try:
            superfn = super().__enter__  # type: ignore
        except AttributeError:
            ret = self
        else:
            ret = superfn()
        self._exit_stack.__enter__()
        return ret

    def __exit__(
            self,
            exc_type: ta.Optional[ta.Type[Exception]],
            exc_val: ta.Optional[Exception],
            exc_tb: ta.Optional[types.TracebackType]
    ) -> ta.Optional[bool]:
        self._exit_stack.__exit__(exc_type, exc_val, exc_tb)
        try:
            superfn = super().__exit__  # type: ignore
        except AttributeError:
            return None
        else:
            return superfn(exc_type, exc_val, exc_tb)


@contextlib.contextmanager
def maybe_managing(obj: T) -> ta.Iterator[T]:
    if isinstance(obj, ContextManageable):
        with obj:
            yield ta.cast(T, obj)
    else:
        yield obj


@contextlib.contextmanager
def disposing(obj: T, attr: str = 'dispose') -> ta.Iterator[T]:
    try:
        yield obj
    finally:
        getattr(obj, attr)()


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Iterator[ta.Callable]:
    try:
        yield fn
    finally:
        fn()


ContextWrappable = ta.Union[ta.ContextManager, str, ta.Callable[..., ta.ContextManager]]


class ContextWrapped:

    def __init__(self, fn: ta.Callable, cm: ta.Union[str, ContextWrappable]) -> None:
        super().__init__()

        self._fn = fn
        self._cm = cm
        self._name = None

        functools.update_wrapper(self, fn)

    def __set_name__(self, owner, name):
        if name is not None:
            if self._name is not None:
                if name != self._name:
                    raise NameError(name, self._name)
            else:
                self._name = name

    def __get__(self, instance, owner=None):
        if instance is None and owner is None:
            return self
        fn = self._fn.__get__(instance, owner)
        cm = self._cm
        if isinstance(self._cm, str):
            if instance is not None:
                cm = getattr(instance, cm)
            elif owner is not None:
                cm = getattr(owner, cm)
            else:
                raise TypeError(cm)
        elif hasattr(cm, '__enter__'):
            pass
        elif callable(cm):
            cm = cm.__get__(instance, owner)
        else:
            raise TypeError(cm)
        ret = type(self)(fn, cm)
        if self._name is not None:
            try:
                instance.__dict__[self._name] = ret
            except TypeError:
                pass
        return ret

    def __call__(self, *args, **kwargs):
        if isinstance(self._cm, str):
            raise TypeError(self._cm)
        cm = self._cm
        if not hasattr(cm, '__enter__') and callable(cm):
            cm = cm(*args, **kwargs)
        with cm:
            return self._fn(*args, **kwargs)


def context_wrapped(cm: ContextWrappable) -> ta.Callable[[CallableT], CallableT]:
    def inner(fn):
        return ContextWrapped(fn, cm)
    return inner


@contextlib.contextmanager
def context_var_setting(var: contextvars.ContextVar[T], val: T) -> ta.Iterator[T]:
    token = var.set(val)
    try:
        yield val
    finally:
        var.reset(token)


def manage_maybe_iterator(
        manager_factory: ta.Callable[[], ta.ContextManager[ta.Any]],
        maybe_iterator_factory: ta.Callable[[], IteratorTOrT]
) -> IteratorTOrT:
    with manager_factory():
        result = maybe_iterator_factory()
    if isinstance(result, collections.abc.Iterator):
        def inner():
            with manager_factory():
                yield from result
        return inner()
    else:
        return result


Lockable = ta.Callable[[], ContextManageable]
DefaultLockable = ta.Union[None, bool, Lockable, ContextManageable]


def default_lock(value: DefaultLockable, default: DefaultLockable) -> Lockable:
    if value is None:
        value = default
    if value is True:
        lock = threading.RLock()
        return lambda: lock  # type: ignore
    elif value is False or value is None:
        return nop_context_manager
    elif callable(value):
        return value
    elif isinstance(value, ContextManageable):
        return lambda: value  # type: ignore
    else:
        raise TypeError(value)


@contextlib.contextmanager
def breakpoint_on_exception():
    try:
        yield
    except Exception as e:  # noqa
        breakpoint()
        raise


@contextlib.contextmanager
def setattr_context(obj, attr, val, *, default=None):
    not_set = object()
    orig = getattr(obj, attr, not_set)
    try:
        setattr(obj, attr, val)
        if orig is not not_set:
            yield orig
        else:
            yield default
    finally:
        if orig is not_set:
            delattr(obj, attr)
        else:
            setattr(obj, attr, orig)
