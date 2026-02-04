import typing as ta

from ... import lang
from ... import reflect as rfl
from .. import Polymorphism
from .types import Impls


##


def get_polymorphism_impls(
        rty: rfl.Type,
        p: Polymorphism,
) -> Impls | None:
    if rty is p.ty:
        return p.impls

    if (
            isinstance(rty, type) and
            lang.is_abstract(rty) and
            p.bases is not None and
            (ib := p.bases.by_ty.get(rty)) is not None
    ):
        return Impls([p.impls.by_ty[a] for a in ib.impl_tys])

    if (
            isinstance(rty, rfl.Union) and
            (u_is := get_polymorphism_union_impls(rty, p)) is not None
    ):
        return u_is

    return None


def get_polymorphism_union_impls(
        rty: rfl.Union,
        p: Polymorphism,
) -> Impls | None:
    if not all(isinstance(a, type) for a in rty.args):
        return None

    ts = ta.cast('set[type]', set(rty.args))

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
