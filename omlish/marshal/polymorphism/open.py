import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value
from .api import Impls
from .api import OpenPolymorphismOptions
from .marshal import PolymorphismMarshaler
from .unmarshal import PolymorphismUnmarshaler


##


class _OpenPolymorphismBase(lang.Abstract):
    def __init__(
            self,
            ty: type,
            opts: OpenPolymorphismOptions = OpenPolymorphismOptions(),
    ) -> None:
        super().__init__()

        self._ty = ty
        self._opts = opts

    def get_impls(self) -> Impls | None:
        return None


class OpenPolymorphismMarshaler(_OpenPolymorphismBase, PolymorphismMarshaler):
    def get_marshaler_map(self) -> ta.Mapping[type, tuple[str, Marshaler]]:
        raise NotImplementedError

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        raise NotImplementedError


class OpenPolymorphismUnmarshaler(_OpenPolymorphismBase, PolymorphismUnmarshaler):
    def get_unmarshaler_map(self) -> ta.Mapping[str, Unmarshaler]:
        raise NotImplementedError

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class OpenPolymorphismMarshalerFactory(MarshalerFactory):
    ty: type
    opts: OpenPolymorphismOptions = OpenPolymorphismOptions()

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if rty != self.ty:
            return None
        return lambda: OpenPolymorphismMarshaler(self.ty, self.opts)


@dc.dataclass(frozen=True)
class OpenPolymorphismUnmarshalerFactory(UnmarshalerFactory):
    ty: type
    opts: OpenPolymorphismOptions = OpenPolymorphismOptions()

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if rty != self.ty:
            return None
        return lambda: OpenPolymorphismUnmarshaler(self.ty, self.opts)
