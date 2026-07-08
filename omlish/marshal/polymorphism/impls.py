import typing as ta

from ... import lang
from ... import reflect2 as rfl
from .api import Impls
from .api import Polymorphism


##


def _root_matches(rty: rfl.Type, key: ta.Any) -> bool:
    if isinstance(key, rfl.Type):
        return rty.type_key_or_none() == key.type_key_or_none() if rty.type_key_or_none() is not None else rty is key

    return rfl.get_runtime_object_or_none(rty) is key


def get_polymorphism_impls(
        rty: rfl.Type,
        p: Polymorphism,
) -> Impls | None:
    if _root_matches(rty, p.root):
        return p.impls

    if (
            (cls := rfl.get_runtime_type_or_none(rty)) is not None and
            lang.is_abstract(cls) and
            p.bases is not None and
            (ib := p.bases.by_ty.get(cls)) is not None
    ):
        return Impls([p.impls.by_ty[a] for a in ib.impl_tys])

    if (
            isinstance(rty, rfl.UnionType) and
            (u_is := get_polymorphism_union_impls(rty, p)) is not None
    ):
        return u_is

    return None


def get_polymorphism_union_impls(
        rty: rfl.UnionType,
        p: Polymorphism,
) -> Impls | None:
    tys = [rfl.get_runtime_type_or_none(it) for it in rty.items]
    if any(t is None for t in tys):
        return None

    ts = ta.cast('set[type]', set(tys))

    if p.bases is not None:
        ts = {
            it
            for t in ts
            for bt in [p.bases.by_ty.get(t)]
            for it in (bt.impl_tys if bt is not None else [t])
        }

    if ts - p.impls.by_ty.keys():
        return None

    return Impls([p.impls.by_ty[a] for a in ts])
