import typing as ta

from .types import Annotated
from .types import Any
from .types import Generic
from .types import NewType
from .types import Type
from .types import Union
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


def get_concrete_type(ty: Type) -> type | None:
    if isinstance(ty, type):
        return ty

    if isinstance(ty, Generic):
        return ty.cls

    if isinstance(ty, NewType):
        return get_concrete_type(get_underlying(ty))

    if isinstance(ty, (Union, ta.TypeVar, Any)):
        return None

    raise TypeError(ty)


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
