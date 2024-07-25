import contextlib
import contextvars
import functools
import threading
import types
import typing as ta


T = ta.TypeVar('T')


##


class ContextManaged:

    def __enter__(self: ta.Self) -> ta.Self:
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        return None


class NopContextManaged(ContextManaged):

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        raise TypeError


NOP_CONTEXT_MANAGED = NopContextManaged()


class NopContextManager:

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        raise TypeError

    def __call__(self, *args, **kwargs):
        return NOP_CONTEXT_MANAGED


NOP_CONTEXT_MANAGER = NopContextManager()


##


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Generator[ta.Callable, None, None]:
    try:
        yield fn
    finally:
        fn()


@contextlib.asynccontextmanager
async def a_defer(fn: ta.Awaitable) -> ta.AsyncGenerator[ta.Awaitable, None]:
    try:
        yield fn
    finally:
        await fn


@contextlib.contextmanager
def maybe_managing(obj: T) -> ta.Iterator[T]:
    if isinstance(obj, ta.ContextManager):
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
def breakpoint_on_exception():  # noqa
    try:
        yield
    except Exception as e:  # noqa
        breakpoint()  # noqa
        raise


@contextlib.contextmanager
def context_var_setting(var: contextvars.ContextVar[T], val: T) -> ta.Iterator[T]:
    token = var.set(val)
    try:
        yield val
    finally:
        var.reset(token)


@contextlib.contextmanager
def attr_setting(obj, attr, val, *, default=None):  # noqa
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


##


class ExitStacked:

    @property
    def _exit_stack(self) -> contextlib.ExitStack:
        try:
            return self.__exit_stack  # type: ignore
        except AttributeError:
            es = self.__exit_stack = contextlib.ExitStack()
            return es

    def _enter_context(self, context_manager: ta.ContextManager[T]) -> T:
        return self._exit_stack.enter_context(ta.cast(ta.ContextManager, context_manager))

    def __enter__(self: ta.Self) -> ta.Self:
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
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        self._exit_stack.__exit__(exc_type, exc_val, exc_tb)
        try:
            superfn = super().__exit__  # type: ignore
        except AttributeError:
            return None
        else:
            return superfn(exc_type, exc_val, exc_tb)


##


ContextWrappable: ta.TypeAlias = ta.ContextManager | str | ta.Callable[..., ta.ContextManager]


class ContextWrapped:

    def __init__(self, fn: ta.Callable, cm: str | ContextWrappable) -> None:
        super().__init__()

        self._fn = (fn,)
        self._cm = cm
        self._name: str | None = None

        functools.update_wrapper(self, fn)

    @property
    def _fn(self):
        return self.__fn

    @_fn.setter
    def _fn(self, x):
        self.__fn = x

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
        fn = self._fn[0].__get__(instance, owner)  # noqa
        cm: ta.Any = self._cm
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
            cm = cm.__get__(instance, owner)  # noqa
        else:
            raise TypeError(cm)
        ret = type(self)(fn, cm)
        if self._name is not None:
            with contextlib.suppress(TypeError):
                instance.__dict__[self._name] = ret
        return ret

    def __call__(self, *args, **kwargs):
        if isinstance(self._cm, str):
            raise TypeError(self._cm)
        cm = self._cm
        if not hasattr(cm, '__enter__') and callable(cm):
            cm = cm(*args, **kwargs)
        with cm:  # type: ignore
            return self._fn[0](*args, **kwargs)


def context_wrapped(cm):  # ContextWrappable -> ta.Callable[[CallableT], CallableT]:  # noqa
    def inner(fn):
        return ContextWrapped(fn, cm)
    return inner


##


Lockable = ta.Callable[[], ta.ContextManager]
DefaultLockable = bool | Lockable | ta.ContextManager | None


def default_lock(value: DefaultLockable, default: DefaultLockable) -> Lockable:
    if value is None:
        value = default
    if value is True:
        lock = threading.RLock()
        return lambda: lock
    elif value is False or value is None:
        return NOP_CONTEXT_MANAGER
    elif callable(value):
        return value
    elif isinstance(value, ta.ContextManager):
        return lambda: value
    else:
        raise TypeError(value)
