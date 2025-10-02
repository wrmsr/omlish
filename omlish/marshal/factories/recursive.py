import typing as ta

from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.values import Value


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
T = ta.TypeVar('T')


##


class _RecursiveFactory(ta.Generic[FactoryT]):
    def __init__(
            self,
            fac: FactoryT,
            prx: ta.Callable[[], tuple[ta.Any, ta.Callable[[ta.Any], None]]],
    ) -> None:
        super().__init__()

        self._fac = fac
        self._prx = prx

        self._dct: dict[rfl.Type, ta.Any] = {}

    def _wrap(self, m, rty):
        def inner():
            try:
                return self._dct[rty]
            except KeyError:
                pass

            p, sp = self._prx()
            self._dct[rty] = p
            try:
                r = m()
                sp(r)
                return r
            finally:
                del self._dct[rty]

        return inner


class _Proxy(ta.Generic[T]):
    __obj: T | None = None

    @property
    def _obj(self) -> T:
        if self.__obj is None:
            raise TypeError('recursive proxy not set')
        return self.__obj

    def _set_obj(self, obj: T) -> None:
        if self.__obj is not None:
            raise TypeError('recursive proxy already set')
        self.__obj = obj

    @classmethod
    def _new(cls) -> tuple[ta.Any, ta.Callable[[ta.Any], None]]:
        return (p := cls()), p._set_obj  # noqa


#


class _ProxyMarshaler(_Proxy[Marshaler], Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self._obj.marshal(ctx, o)


class RecursiveMarshalerFactory(_RecursiveFactory[MarshalerFactory], MarshalerFactory):
    def __init__(self, fac: MarshalerFactory) -> None:
        super().__init__(fac, _ProxyMarshaler._new)  # noqa

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (m := self._fac.make_marshaler(ctx, rty)) is None:
            return None
        return self._wrap(m, rty)


#


class _ProxyUnmarshaler(_Proxy[Unmarshaler], Unmarshaler):
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self._obj.unmarshal(ctx, v)


class RecursiveUnmarshalerFactory(_RecursiveFactory[UnmarshalerFactory], UnmarshalerFactory):
    def __init__(self, fac: UnmarshalerFactory) -> None:
        super().__init__(fac, _ProxyUnmarshaler._new)  # noqa

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (m := self._fac.make_unmarshaler(ctx, rty)) is None:
            return None
        return self._wrap(m, rty)
