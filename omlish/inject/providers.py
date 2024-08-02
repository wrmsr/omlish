import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .elements import Element
from .elements import Elements
from .impl.inspect import signature
from .keys import Key
from .keys import as_key


class _Missing(lang.NotInstantiable):
    pass


##


class Provider(lang.Abstract):
    @abc.abstractmethod
    def provided_ty(self) -> rfl.Type | None:
        raise NotImplementedError


##


def as_provider(o: ta.Any) -> Provider:
    check.not_isinstance(o, (Element, Elements))
    if isinstance(o, Provider):
        return o
    if isinstance(o, Key):
        return link(o)
    if isinstance(o, type):
        return ctor(o)
    if callable(o):
        return fn(o)
    return const(o)


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class FnProvider(Provider):
    fn: ta.Any = dc.xfield(check=callable)
    ty: rfl.Type | None = None

    def provided_ty(self) -> rfl.Type | None:
        return self.ty


def fn(fn: ta.Any, ty: rfl.Type | None = _Missing) -> Provider:
    check.not_isinstance(fn, type)
    check.callable(fn)
    if ty is _Missing:
        sig = signature(fn)
        ty = rfl.type_(sig.return_annotation)
    return FnProvider(fn, ty)


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class CtorProvider(Provider):
    ty: type = dc.xfield(coerce=check.of_isinstance(type))

    def provided_ty(self) -> type:
        return self.ty


def ctor(ty: type) -> Provider:
    check.isinstance(ty, type)
    return CtorProvider(ty)


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ConstProvider(Provider):
    v: ta.Any
    ty: rfl.Type | None = None

    def provided_ty(self) -> rfl.Type | None:
        return self.ty


def const(v: ta.Any, ty: rfl.Type | None = _Missing) -> Provider:
    if ty is _Missing:
        ty = type(v)
    return ConstProvider(v, ty)


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class LinkProvider(Provider):
    k: Key = dc.xfield(coerce=check.of_isinstance(Key))

    def provided_ty(self) -> rfl.Type | None:
        return None


def link(k: ta.Any) -> Provider:
    return LinkProvider(as_key(k))
