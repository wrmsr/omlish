"""
TODO:
 - auto-gen from __subclasses__ if abstract
  - cfg: unless prefixed with _ or abstract
 - auto-name
"""
import dataclasses as dc
import typing as ta

from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


@dc.dataclass(frozen=True)
class Impl:
    ty: type
    tag: str
    alts: ta.AbstractSet[str] = frozenset()


class Polymorphism:
    def __init__(self, ty: type, impls: ta.Iterable[Impl]) -> None:
        super().__init__()
        self._ty = ty
        self._impls = list(impls)

        by_ty: dict[type, Impl] = {}
        by_tag: dict[str, Impl] = {}
        for i in self._impls:
            if not issubclass(i.ty, ty) or i.ty in by_ty:
                raise TypeError(i.ty, ty)
            if i.tag in by_tag:
                raise NameError(i.tag)
            for a in i.alts:
                if a in by_tag:
                    raise NameError(a)
            by_ty[i.ty] = i
            by_tag[i.tag] = i
            for a in i.alts:
                by_tag[a] = i
        self._by_ty = by_ty
        self._by_tag = by_tag

    @property
    def ty(self) -> type:
        return self._ty

    @property
    def impls(self) -> ta.Sequence[Impl]:
        return self._impls

    @property
    def by_ty(self) -> ta.Mapping[type, Impl]:
        return self._by_ty

    @property
    def by_tag(self) -> ta.Mapping[str, Impl]:
        return self._by_tag


@dc.dataclass(frozen=True)
class PolymorphismMarshaler(Marshaler):
    m: ta.Mapping[type, tuple[str, Marshaler]]

    def marshal(self, ctx: MarshalContext, o: ta.Optional[ta.Any]) -> Value:
        tag, m = self.m[type(o)]
        return {tag: m.marshal(ctx, o)}


@dc.dataclass(frozen=True)
class PolymorphismMarshalerFactory(MarshalerFactory):
    p: Polymorphism

    def __call__(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Optional[Marshaler]:
        if rty is self.p.ty:
            return PolymorphismMarshaler({
                i.ty: (i.tag, ctx.make(i.ty))
                for i in self.p.impls
            })
        return None


@dc.dataclass(frozen=True)
class PolymorphismUnmarshaler(Unmarshaler):
    m: ta.Mapping[str, Unmarshaler]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Optional[ta.Any]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PolymorphismUnmarshalerFactory(UnmarshalerFactory):
    p: Polymorphism

    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if rty is self.p.ty:
            return PolymorphismUnmarshaler({
                t: u
                for i in self.p.impls
                for u in [ctx.make(i.ty)]
                for t in [i.tag, *i.alts]
            })
        return None
