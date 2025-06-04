import typing as ta

from .types import Annotated
from .types import Any
from .types import Generic
from .types import NewType
from .types import Type
from .types import Union
from .types import get_type_var_bound
from .types import type_


def strip_objs(ty: Type) -> Type:
    if isinstance(ty, (type, ta.TypeVar, NewType, Any)):
        return ty

    if isinstance(ty, Union):
        return Union(frozenset(map(strip_objs, ty.args)))

    if isinstance(ty, Generic):
        return Generic(ty.cls, tuple(map(strip_objs, ty.args)), ty.params, None)

    if isinstance(ty, Annotated):
        return Annotated(strip_objs(ty.ty), ty.md, None)

    raise TypeError(ty)


def strip_annotations(ty: Type) -> Type:
    if isinstance(ty, (type, ta.TypeVar, NewType, Any)):
        return ty

    if isinstance(ty, Union):
        return Union(frozenset(map(strip_annotations, ty.args)))

    if isinstance(ty, Generic):
        return Generic(ty.cls, tuple(map(strip_annotations, ty.args)), ty.params, ty.obj)

    if isinstance(ty, Annotated):
        return strip_annotations(ty.ty)

    raise TypeError(ty)


def types_equivalent(l: Type, r: Type) -> bool:
    if isinstance(l, Generic) and isinstance(r, Generic):
        return l.cls == r.cls and l.args == r.args

    return l == r


def get_underlying(nt: NewType) -> Type:
    return type_(nt.obj.__supertype__)  # noqa


def get_concrete_type(
        ty: Type,
        *,
        use_type_var_bound: bool = False,
) -> type | None:
    def rec(cur: Type) -> type | None:
        if isinstance(cur, type):
            return cur

        if isinstance(cur, Generic):
            return cur.cls

        if isinstance(cur, NewType):
            return rec(get_underlying(cur))

        if isinstance(cur, ta.TypeVar):
            if use_type_var_bound is not None and (tvb := get_type_var_bound(cur)) is not None:
                return rec(type_(tvb))

            return None

        if isinstance(cur, (Union, Any)):
            return None

        raise TypeError(cur)

    return rec(ty)


def to_annotation(ty: Type) -> ta.Any:
    if isinstance(ty, Generic):
        return ty.obj if ty.obj is not None else ty.cls

    if isinstance(ty, Union):
        return ta.Union[*tuple(to_annotation(e) for e in ty.args)]

    if isinstance(ty, (type, ta.TypeVar, NewType)):
        return ty

    if isinstance(ty, Any):
        return ta.Any

    raise TypeError(ty)
