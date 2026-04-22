import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import Override


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)


##


class _OverrideFactory(lang.Abstract, ta.Generic[FactoryT]):
    def __init__(self, fac: FactoryT) -> None:
        super().__init__()

        self._fac = fac


class OverrideMarshalerFactory(_OverrideFactory[MarshalerFactory], MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (ovr_lst := ctx.configs.get_of(rty, Override)):
            return self._fac.make_marshaler(ctx, rty)

        ovr = check.single(ovr_lst)

        if (ovo := ovr.marshaler) is not None:
            return lambda: ovo

        if ovr.marshaler_factory is not None:
            if (ovf := ovr.marshaler_factory.make_marshaler(ctx, rty)) is not None:
                return ovf

            if not ovr.fallback:
                return None

        return self._fac.make_marshaler(ctx, rty)


class OverrideUnmarshalerFactory(_OverrideFactory[UnmarshalerFactory], UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (ovr_lst := ctx.configs.get_of(rty, Override)):
            return self._fac.make_unmarshaler(ctx, rty)

        ovr = check.single(ovr_lst)

        if (ovo := ovr.unmarshaler) is not None:
            return lambda: ovo

        if ovr.unmarshaler_factory is not None:
            if (ovf := ovr.unmarshaler_factory.make_unmarshaler(ctx, rty)) is not None:
                return ovf

            if not ovr.fallback:
                return None

        return self._fac.make_unmarshaler(ctx, rty)
