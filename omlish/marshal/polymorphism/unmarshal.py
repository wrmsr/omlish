import abc
import collections.abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value
from .api import FieldTypeTagging
from .api import Impls
from .api import Polymorphism
from .api import TypeTagging
from .api import WrapperTypeTagging
from .impls import get_polymorphism_impls


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
        ctx: UnmarshalFactoryContext,
) -> Unmarshaler:
    check.not_empty(impls)

    m = {
        t: u
        for i in impls
        for u in [ctx.make_unmarshaler(i.ty)]
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

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (impls := get_polymorphism_impls(rty, self.p)) is None:
            return None
        return lambda: make_polymorphism_unmarshaler(impls, self.tt, ctx)
