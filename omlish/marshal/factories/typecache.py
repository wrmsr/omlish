import typing as ta

from ... import check
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


class _TypeCacheFactory(ta.Generic[FactoryT]):
    def __init__(self, fac: FactoryT) -> None:
        super().__init__()

        self._fac = fac

        self._dct: dict[rfl.Type, ta.Any | None] = {}

    def _make(self, cfgs, rty, dfl):
        check.isinstance(rty, rfl.TYPES)

        try:
            return self._dct[rty]
        except KeyError:
            pass

        with cfgs._lock:  # noqa
            try:
                return self._dct[rty]
            except KeyError:
                pass

            if (m := dfl()) is None:
                self._dct[rty] = None
                return None

            x = None

            def inner():
                nonlocal x
                if x is None:
                    x = m()
                return x

            self._dct[rty] = inner
            return inner


class TypeCacheMarshalerFactory(_TypeCacheFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._make(ctx.configs, rty, lambda: self._fac.make_marshaler(ctx, rty))


class TypeCacheUnmarshalerFactory(_TypeCacheFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._make(ctx.configs, rty, lambda: self._fac.make_unmarshaler(ctx, rty))
