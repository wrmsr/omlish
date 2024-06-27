import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elements
from .impl.inspect import signature
from .keys import Key
from .keys import as_key
from .types import Cls


class _Missing(lang.NotInstantiable):
    pass


##


class Provider(lang.Abstract):
    @abc.abstractmethod
    def provided_cls(self) -> Cls | None:
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


@dc.dataclass(frozen=True, eq=False)
class FnProvider(Provider):
    fn: ta.Any
    cls: Cls | None = None

    def provided_cls(self) -> Cls | None:
        return self.cls


def fn(fn: ta.Any, cls: ta.Optional[Cls] = _Missing) -> Provider:
    check.not_isinstance(fn, type)
    check.callable(fn)
    if cls is _Missing:
        sig = signature(fn)
        cls = check.isinstance(sig.return_annotation, type)
    return FnProvider(fn, cls)


##


@dc.dataclass(frozen=True, eq=False)
class CtorProvider(Provider):
    cls: type

    def provided_cls(self) -> Cls:
        return self.cls


def ctor(cls: type) -> Provider:
    check.isinstance(cls, type)
    return CtorProvider(cls)


##


@dc.dataclass(frozen=True, eq=False)
class ConstProvider(Provider):
    v: ta.Any
    cls: Cls | None = None

    def provided_cls(self) -> Cls | None:
        return self.cls


def const(v: ta.Any, cls: ta.Optional[Cls] = _Missing) -> Provider:
    if cls is _Missing:
        cls = type(v)
    return ConstProvider(v, cls)


##


@dc.dataclass(frozen=True, eq=False)
class LinkProvider(Provider):
    k: Key

    def provided_cls(self) -> Cls | None:
        return None


def link(k: ta.Any) -> Provider:
    return LinkProvider(as_key(k))
