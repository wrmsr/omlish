import threading
import typing as ta

from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import BaseContext
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import MarshalerMaker
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.types import UnmarshalerMaker


R = ta.TypeVar('R')
ContextT = ta.TypeVar('ContextT', bound=BaseContext)


##


class _InvalidatableFactory(mfs.MatchFn[[ContextT, rfl.Type], R]):
    def __init__(
            self,
            fn: ta.Callable[[], mfs.MatchFn[[ContextT, rfl.Type], R]],
            check_fn: ta.Callable[[], bool] | None = None,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._check_fn: ta.Callable[[], bool] | None = check_fn

        self._lock = threading.RLock()

    #

    _f_: mfs.MatchFn[[ContextT, rfl.Type], R] | None = None

    def _invalidate(self) -> None:
        self._f_ = None

    def invalidate(self) -> None:
        with self._lock:
            self._invalidate()

    def _maybe_invalidate(self) -> None:
        if self._check_fn is not None:
            if self._check_fn():
                with self._lock:
                    if self._check_fn():
                        self._invalidate()

    def _f(self) -> mfs.MatchFn[[ContextT, rfl.Type], R]:
        self._maybe_invalidate()

        if (f := self._f_) is None:
            with self._lock:
                if (f := self._f_) is None:
                    f = self._f_ = self._fn()

        return f

    #

    def guard(self, ctx: ContextT, rty: rfl.Type) -> bool:
        return self._f().guard(ctx, rty)

    def fn(self, ctx: ContextT, rty: rfl.Type) -> R:
        return self._f()(ctx, rty)


##


class InvalidatableMarshalerFactory(MarshalerFactory):
    def __init__(
            self,
            fn: ta.Callable[[], MarshalerFactory],
            check_fn: ta.Callable[[], bool] | None = None,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._u: _InvalidatableFactory[MarshalContext, Marshaler] = _InvalidatableFactory(
            lambda: fn().make_marshaler,
            check_fn,
        )

    def invalidate(self) -> None:
        self._u.invalidate()

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._u


class InvalidatableUnmarshalerFactory(UnmarshalerFactory):
    def __init__(
            self,
            fn: ta.Callable[[], UnmarshalerFactory],
            check_fn: ta.Callable[[], bool] | None = None,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._u: _InvalidatableFactory[UnmarshalContext, Unmarshaler] = _InvalidatableFactory(
            lambda: fn().make_unmarshaler,
            check_fn,
        )

    def invalidate(self) -> None:
        self._u.invalidate()

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._u
