"""
Dynamically scoped variables (implemented by stackwalking). Unlike threadlocals these are generator-correct both in
binding and retrieval, and unlike ContextVars they require no manual context management. They are however *slow* and
should be used sparingly (once per sql statement executed not once per inner function call).

TODO:
 - clj-style binding conveyance
 - contextvar/async interop
 - 'partializer'
"""
import contextlib
import functools
import sys
import types
import typing as ta
import weakref

from . import lang


T = ta.TypeVar('T')


##


_HOISTED_CODE_DEPTH: ta.MutableMapping[types.CodeType, int] = weakref.WeakKeyDictionary()
_MAX_HOIST_DEPTH = 0


def hoist(depth=0):  # noqa
    def inner(fn):
        _HOISTED_CODE_DEPTH[fn.__code__] = depth
        global _MAX_HOIST_DEPTH
        _MAX_HOIST_DEPTH = max(_MAX_HOIST_DEPTH, depth)
        return fn
    return inner


hoist()(contextlib.ExitStack.enter_context)  # noqa


class MISSING(lang.Marker):
    pass


class UnboundVarError(ValueError):
    pass


class Var(ta.Generic[T]):
    def __init__(
            self,
            default: type[MISSING] | T = MISSING,
            *,
            new: ta.Callable[[], T] | type[MISSING] = MISSING,
            validate: ta.Callable[[T], None] | None = None,
    ) -> None:
        super().__init__()

        if default is not MISSING and new is not MISSING:
            raise TypeError('Cannot set both default and new')
        elif default is not MISSING:
            new = lambda: default  # type: ignore
        self._new: type[MISSING] | ta.Callable[[], T] = new
        self._validate = validate
        self._bindings_by_frame: ta.MutableMapping[types.FrameType, ta.MutableMapping[int, Binding]] = weakref.WeakValueDictionary()  # noqa

    @ta.overload
    def __call__(self) -> T:
        ...

    @ta.overload
    def __call__(self, value: T, **kwargs: ta.Any) -> ta.ContextManager[T]:
        ...

    def __call__(self, *args, **kwargs):
        if not args:
            if kwargs:
                raise TypeError(kwargs)
            return self.value
        elif len(args) == 1:
            return self.binding(*args, **kwargs)
        else:
            raise TypeError(args)

    def binding(self, value: T, *, offset: int = 0) -> ta.ContextManager[T]:
        if self._validate is not None:
            self._validate(self.value)
        return Binding(self, value, offset=offset)

    def with_binding(self, value):  # noqa
        def outer(fn):
            @functools.wraps(fn)
            def inner(*args, **kwargs):
                with self.binding(value):
                    return fn(*args, **kwargs)
            return inner
        return outer

    def with_binding_fn(self, binding_fn):  # noqa
        this = self

        def outer(fn):
            class Descriptor:
                @staticmethod
                @functools.wraps(fn)
                def __call__(*args, **kwargs):  # noqa
                    with this.binding(binding_fn(*args, **kwargs)):
                        return fn(*args, **kwargs)

                def __get__(self, obj, cls=None):
                    bound_binding_fn = binding_fn.__get__(obj, cls)
                    bound_fn = fn.__get__(obj, cls)

                    @functools.wraps(fn)
                    def inner(*args, **kwargs):
                        with this.binding(bound_binding_fn(*args, **kwargs)):
                            return bound_fn(*args, **kwargs)

                    return inner

            dct: dict[str, ta.Any] = {k: getattr(fn, k) for k in functools.WRAPPER_ASSIGNMENTS}
            return lang.new_type(fn.__name__, (Descriptor,), dct)()

        return outer

    @property
    def values(self) -> ta.Iterator[T]:
        frame = sys._getframe().f_back  # noqa
        while frame:
            try:
                frame_bindings = self._bindings_by_frame[frame]
            except KeyError:
                pass
            else:
                for level, frame_binding in sorted(frame_bindings.items()):  # noqa
                    yield frame_binding._value  # noqa
            frame = frame.f_back

        if self._new is not MISSING:
            yield self._new()  # type: ignore

    def __iter__(self) -> ta.Iterator[T]:
        return self.values

    @property
    def value(self) -> T:
        try:
            return next(self.values)
        except StopIteration:
            raise UnboundVarError from None


class Binding(ta.Generic[T]):
    _frame: types.FrameType
    _frame_bindings: ta.MutableMapping[int, 'Binding']
    _level: int

    def __init__(self, var: Var[T], value: T, *, offset: int = 0) -> None:
        super().__init__()

        self._var = var
        self._value = value
        self._offset = offset

    def __enter__(self) -> T:
        frame = sys._getframe(self._offset).f_back  # noqa
        lag_frame: types.FrameType | None = frame
        while lag_frame is not None:
            for cur_depth in range(_MAX_HOIST_DEPTH + 1):
                if lag_frame is None:
                    break
                try:
                    lag_hoist = _HOISTED_CODE_DEPTH[lag_frame.f_code]
                except KeyError:
                    pass
                else:
                    if lag_hoist >= cur_depth:
                        frame = lag_frame = lag_frame.f_back
                        break
                lag_frame = lag_frame.f_back
            else:
                break

        if frame is None:
            raise RuntimeError
        self._frame = frame
        try:
            self._frame_bindings = self._var._bindings_by_frame[self._frame]  # noqa
        except KeyError:
            self._frame_bindings = self._var._bindings_by_frame[self._frame] = weakref.WeakValueDictionary()  # noqa
            self._level = 0
        else:
            self._level = min(self._frame_bindings.keys() or [1]) - 1

        self._frame_bindings[self._level] = self
        return self._value

    def __exit__(self, et, e, tb):
        if self._frame_bindings[self._level] is not self:
            raise TypeError

        del self._frame_bindings[self._level]
        del self._frame_bindings
        del self._frame


class _GeneratorContextManager(contextlib._GeneratorContextManager):  # noqa
    @hoist(2)
    def __enter__(self):
        return super().__enter__()


def contextmanager(fn):  # noqa
    @functools.wraps(fn)
    def helper(*args, **kwds):
        return _GeneratorContextManager(fn, args, kwds)
    return helper  # noqa
