import abc
import dataclasses as dc
import typing as ta

from ... import lang
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.values import Value
from .metadata import FieldTypeTagging
from .metadata import Impls
from .metadata import Polymorphism
from .metadata import TypeTagging
from .metadata import WrapperTypeTagging


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
        if rty is not self.p.ty:
            return None
        return lambda: make_polymorphism_marshaler(self.p.impls, self.tt, ctx)
