import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .keys import Key


class _Missing(lang.NotInstantiable):
    pass


class Provider(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class FnProvider(Provider):
    fn: ta.Any = dc.xfield(validate=callable)


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class CtorProvider(Provider):
    ty: type = dc.xfield(coerce=check.of_isinstance(type))


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ConstProvider(Provider):
    v: ta.Any


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class LinkProvider(Provider):
    k: Key = dc.xfield(coerce=check.of_isinstance(Key))
