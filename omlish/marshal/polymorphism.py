"""
TODO:
 - auto-gen from __subclasses__ if abstract
  - cfg: unless prefixed with _ or abstract
  - iff Sealed
 - auto-name
"""
import collections.abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import lang
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .naming import Naming
from .naming import translate_name
from .registries import RegistryItem
from .values import Value


##


class TypeTagging(RegistryItem, lang.Abstract, lang.Sealed):
    pass


class WrapperTypeTagging(TypeTagging, lang.Final):
    pass


@dc.dataclass(frozen=True)
class FieldTypeTagging(TypeTagging, lang.Final):
    field: str


##


@dc.dataclass(frozen=True)
class Impl:
    ty: type
    tag: str
    alts: ta.AbstractSet[str] = frozenset()


class Polymorphism:
    def __init__(
            self,
            ty: type,
            impls: ta.Iterable[Impl],
    ) -> None:
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


def polymorphism_from_subclasses(
        ty: type,
        *,
        naming: Naming | None = None,
        strip_suffix: bool = False,
) -> Polymorphism:
    dct: dict[str, Impl] = {}

    seen: set[type] = set()
    todo: list[type] = [ty]
    while todo:
        cur = todo.pop()
        seen.add(cur)

        todo.extend(nxt for nxt in cur.__subclasses__() if nxt not in seen)

        if lang.is_abstract_class(cur):
            continue

        name = cur.__name__
        if strip_suffix:
            name = lang.strip_suffix(name, ty.__name__)
        if naming is not None:
            name = translate_name(name, naming)
        if name in dct:
            raise KeyError(f'Duplicate name: {name}')

        dct[name] = Impl(
            cur,
            name,
        )

    return Polymorphism(ty, dct.values())


##


@dc.dataclass(frozen=True)
class WrapperPolymorphismMarshaler(Marshaler):
    m: ta.Mapping[type, tuple[str, Marshaler]]

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        tag, m = self.m[type(o)]
        return {tag: m.marshal(ctx, o)}


@dc.dataclass(frozen=True)
class FieldPolymorphismMarshaler(Marshaler):
    m: ta.Mapping[type, tuple[str, Marshaler]]
    tf: str

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        tag, m = self.m[type(o)]
        return {self.tf: tag, **m.marshal(ctx, o)}  # type: ignore


@dc.dataclass(frozen=True)
class PolymorphismMarshalerFactory(MarshalerFactory):
    p: Polymorphism
    tt: TypeTagging = WrapperTypeTagging()

    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return rty is self.p.ty

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        check.is_(rty, self.p.ty)
        m = {
            i.ty: (i.tag, ctx.make(i.ty))
            for i in self.p.impls
        }
        if isinstance(self.tt, WrapperTypeTagging):
            return WrapperPolymorphismMarshaler(m)
        elif isinstance(self.tt, FieldTypeTagging):
            return FieldPolymorphismMarshaler(m, self.tt.field)
        else:
            raise TypeError(self.tt)


##


@dc.dataclass(frozen=True)
class WrapperPolymorphismUnmarshaler(Unmarshaler):
    m: ta.Mapping[str, Unmarshaler]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        ma = check.isinstance(v, collections.abc.Mapping)
        [(tag, iv)] = ma.items()
        u = self.m[tag]
        return u.unmarshal(ctx, iv)


@dc.dataclass(frozen=True)
class FieldPolymorphismUnmarshaler(Unmarshaler):
    m: ta.Mapping[str, Unmarshaler]
    tf: str

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        ma = dict(check.isinstance(v, collections.abc.Mapping))
        tag = ma.pop(self.tf)
        u = self.m[tag]
        return u.unmarshal(ctx, ma)


@dc.dataclass(frozen=True)
class PolymorphismUnmarshalerFactory(UnmarshalerFactory):
    p: Polymorphism
    tt: TypeTagging = WrapperTypeTagging()

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return rty is self.p.ty

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        check.is_(rty, self.p.ty)
        m = {
            t: u
            for i in self.p.impls
            for u in [ctx.make(i.ty)]
            for t in [i.tag, *i.alts]
        }
        if isinstance(self.tt, WrapperTypeTagging):
            return WrapperPolymorphismUnmarshaler(m)
        elif isinstance(self.tt, FieldTypeTagging):
            return FieldPolymorphismUnmarshaler(m, self.tt.field)
        else:
            raise TypeError(self.tt)
