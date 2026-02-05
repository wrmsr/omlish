import abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.values import Value
from .api import FieldTypeTagging
from .api import Impls
from .api import Polymorphism
from .api import TypeTagging
from .api import WrapperTypeTagging
from .impls import get_polymorphism_impls


##


class PolymorphismMarshaler(Marshaler, lang.Abstract):
    @abc.abstractmethod
    def get_impls(self) -> ta.Mapping[type, tuple[str, Marshaler]]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class WrapperPolymorphismMarshaler(PolymorphismMarshaler):
    m: ta.Mapping[type, tuple[str, Marshaler]]

    def get_impls(self) -> ta.Mapping[type, tuple[str, Marshaler]]:
        return self.m

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        tag, m = self.m[type(o)]
        return {tag: m.marshal(ctx, o)}


@dc.dataclass(frozen=True)
class FieldPolymorphismMarshaler(PolymorphismMarshaler):
    m: ta.Mapping[type, tuple[str, Marshaler]]
    tf: str

    def get_impls(self) -> ta.Mapping[type, tuple[str, Marshaler]]:
        return self.m

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        tag, m = self.m[type(o)]
        return {self.tf: tag, **m.marshal(ctx, o)}  # type: ignore


def make_polymorphism_marshaler(
        impls: Impls,
        tt: TypeTagging,
        ctx: MarshalFactoryContext,
) -> Marshaler:
    check.not_empty(impls)

    m = {
        i.ty: (i.tag, ctx.make_marshaler(i.ty))
        for i in impls
    }

    if isinstance(tt, WrapperTypeTagging):
        return WrapperPolymorphismMarshaler(m)
    elif isinstance(tt, FieldTypeTagging):
        return FieldPolymorphismMarshaler(m, tt.field)
    else:
        raise TypeError(tt)


@dc.dataclass(frozen=True)
class PolymorphismMarshalerFactory(MarshalerFactory):
    p: Polymorphism
    tt: TypeTagging = WrapperTypeTagging()

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (impls := get_polymorphism_impls(rty, self.p)) is None:
            return None
        return lambda: make_polymorphism_marshaler(impls, self.tt, ctx)
