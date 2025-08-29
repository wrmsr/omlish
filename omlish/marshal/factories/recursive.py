import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import MarshalerMaker
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.types import UnmarshalerMaker
from ..base.values import Value


T = ta.TypeVar('T')
R = ta.TypeVar('R')
C = ta.TypeVar('C')


##


class _RecursiveTypeFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(
            self,
            f: mfs.MatchFn[[C, rfl.Type], R],
            prx: ta.Callable[[], tuple[R, ta.Callable[[R], None]]],
    ) -> None:
        super().__init__()

        self._f = f
        self._prx = prx
        self._dct: dict[rfl.Type, R] = {}

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        check.isinstance(rty, rfl.TYPES)
        return self._f.guard(ctx, rty)

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        check.isinstance(rty, rfl.TYPES)
        try:
            return self._dct[rty]
        except KeyError:
            pass
        p, sp = self._prx()
        self._dct[rty] = p
        try:
            r = self._f(ctx, rty)
            sp(r)
            return r
        finally:
            del self._dct[rty]


##


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


##


class _ProxyMarshaler(_Proxy[Marshaler], Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self._obj.marshal(ctx, o)


class RecursiveMarshalerFactory(MarshalerFactory, lang.Final):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._rtf: _RecursiveTypeFactory[MarshalContext, Marshaler] = _RecursiveTypeFactory(
            self._f.make_marshaler,  # noqa
            _ProxyMarshaler._new,  # noqa
        )

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._rtf


class _ProxyUnmarshaler(_Proxy[Unmarshaler], Unmarshaler):
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self._obj.unmarshal(ctx, v)


class RecursiveUnmarshalerFactory(UnmarshalerFactory, lang.Final):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._rtf: _RecursiveTypeFactory[UnmarshalContext, Unmarshaler] = _RecursiveTypeFactory(
            self._f.make_unmarshaler,  # noqa
            _ProxyUnmarshaler._new,  # noqa
        )

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._rtf
