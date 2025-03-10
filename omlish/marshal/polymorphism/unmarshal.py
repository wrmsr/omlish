import abc
import collections.abc
import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..base import UnmarshalerFactory
from ..values import Value
from .metadata import FieldTypeTagging
from .metadata import Impls
from .metadata import Polymorphism
from .metadata import TypeTagging
from .metadata import WrapperTypeTagging


##


class PolymorphismUnmarshaler(Unmarshaler, lang.Abstract):
    @abc.abstractmethod
    def get_impls(self) -> ta.Mapping[str, Unmarshaler]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class WrapperPolymorphismUnmarshaler(PolymorphismUnmarshaler):
    m: ta.Mapping[str, Unmarshaler]

    def get_impls(self) -> ta.Mapping[str, Unmarshaler]:
        return self.m

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        ma = check.isinstance(v, collections.abc.Mapping)
        [(tag, iv)] = ma.items()
        u = self.m[tag]
        return u.unmarshal(ctx, iv)


@dc.dataclass(frozen=True)
class FieldPolymorphismUnmarshaler(PolymorphismUnmarshaler):
    m: ta.Mapping[str, Unmarshaler]
    tf: str

    def get_impls(self) -> ta.Mapping[str, Unmarshaler]:
        return self.m

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        ma = dict(check.isinstance(v, collections.abc.Mapping))
        tag = ma.pop(self.tf)
        u = self.m[tag]
        return u.unmarshal(ctx, ma)


def make_polymorphism_unmarshaler(
        impls: Impls,
        tt: TypeTagging,
        ctx: UnmarshalContext,
) -> Unmarshaler:
    m = {
        t: u
        for i in impls
        for u in [ctx.make(i.ty)]
        for t in [i.tag, *i.alts]
    }
    if isinstance(tt, WrapperTypeTagging):
        return WrapperPolymorphismUnmarshaler(m)
    elif isinstance(tt, FieldTypeTagging):
        return FieldPolymorphismUnmarshaler(m, tt.field)
    else:
        raise TypeError(tt)


@dc.dataclass(frozen=True)
class PolymorphismUnmarshalerFactory(UnmarshalerFactory):
    p: Polymorphism
    tt: TypeTagging = WrapperTypeTagging()

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return rty is self.p.ty

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        check.is_(rty, self.p.ty)
        return make_polymorphism_unmarshaler(self.p.impls, self.tt, ctx)
