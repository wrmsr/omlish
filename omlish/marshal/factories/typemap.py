import typing as ta

from ... import check
from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


T = ta.TypeVar('T')

FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
HandlerT = ta.TypeVar('HandlerT', bound=Marshaler | Unmarshaler)


##


class _TypeMapFactory(ta.Generic[FactoryT, HandlerT]):
    def __init__(self, m: ta.Mapping[ta.Any, FactoryT | HandlerT]) -> None:
        super().__init__()

        self._dct: ta.Mapping[rfl.TypeKey, FactoryT | HandlerT] = dict(  # noqa
            (
                # FIXME: This does *not* use a marshal context mirror because it doesn't have one.
                rfl.reflect_type(k).type_key(),
                check.isinstance(v, self._value_types),
            )
            for k, v in m.items()
        )

    _value_types: ta.ClassVar[tuple[type, ...]]


class TypeMapMarshalerFactory(_TypeMapFactory[MarshalerFactory, Marshaler], MarshalerFactory):
    _value_types = (MarshalerFactory, Marshaler)

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        check.isinstance(rty, rfl.Type)
        try:
            m = self._dct[rty.type_key()]
        except KeyError:
            return None

        if isinstance(m, Marshaler):
            return lambda: m
        elif isinstance(m, MarshalerFactory):
            return m.make_marshaler(ctx, rty)
        else:
            raise TypeError(m)


class TypeMapUnmarshalerFactory(_TypeMapFactory[UnmarshalerFactory, Unmarshaler], UnmarshalerFactory):
    _value_types = (UnmarshalerFactory, Unmarshaler)

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        check.isinstance(rty, rfl.Type)
        try:
            u = self._dct[rty.type_key()]
        except KeyError:
            return None

        if isinstance(u, Unmarshaler):
            return lambda: u
        elif isinstance(u, UnmarshalerFactory):
            return u.make_unmarshaler(ctx, rty)
        else:
            raise TypeError(u)
