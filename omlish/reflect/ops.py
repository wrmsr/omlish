"""
TODO:
 - visitor / transformer
  - gson had an ObjectNavigator:
   - https://github.com/google/gson/blob/f291c4d33ea5fcc52afcfa5713e519e663378bda/gson/src/main/java/com/google/gson/ObjectNavigator.java
   - removed in 25c6ae177b1ca56db7f3c29eb574bdd032a06165
 - uniform collection isinstance - items() for mappings, iter() for other
 - also check instance type in isinstance not just items lol
"""  # noqa
import dataclasses as dc
import typing as ta

from .types import Annotated
from .types import Any
from .types import Generic
from .types import GenericLike
from .types import NewType
from .types import Protocol
from .types import Type
from .types import Union
from .types import get_type_var_bound
from .types import type_


##


def strip_objs(ty: Type) -> Type:
    if isinstance(ty, (type, ta.TypeVar, NewType, Any)):
        return ty

    if isinstance(ty, Union):
        return dc.replace(ty, args=frozenset(map(strip_objs, ty.args)))

    if isinstance(ty, GenericLike):
        return dc.replace(ty, args=tuple(map(strip_objs, ty.args)), obj=None)

    if isinstance(ty, Annotated):
        return dc.replace(ty, ty=strip_objs(ty.ty), obj=None)

    raise TypeError(ty)


def strip_annotations(ty: Type) -> Type:
    if isinstance(ty, (type, ta.TypeVar, NewType, Any)):
        return ty

    if isinstance(ty, Union):
        return dc.replace(ty, args=frozenset(map(strip_annotations, ty.args)))

    if isinstance(ty, GenericLike):
        return dc.replace(ty, args=tuple(map(strip_annotations, ty.args)))

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

        if isinstance(cur, (Union, Any, Protocol)):
            return None

        raise TypeError(cur)

    return rec(ty)


def to_annotation(ty: Type) -> ta.Any:
    if isinstance(ty, Generic):
        return ty.obj if ty.obj is not None else ty.cls

    if isinstance(ty, Union):
        return ta.Union[*tuple(to_annotation(e) for e in ty.args)]

    if isinstance(ty, Protocol):
        return ta.Protocol[*ty.params]

    if isinstance(ty, (type, ta.TypeVar, NewType)):
        return ty

    if isinstance(ty, Any):
        return ta.Any

    raise TypeError(ty)
